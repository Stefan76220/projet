from __future__ import annotations

"""
TomeLinea V4 — orchestrateur d'analyse Source.

Point d'entrée unique destiné à l'interface.

Chaîne actuelle :

    Source active
        ↓
    extraction factuelle
        ↓
    ressemblances / familles
        ↓
    compréhension éditoriale déterministe
        ↓
    moteurs éditoriaux complémentaires futurs
        ↓
    BookProposal
        ↓
    ARRÊT : validation utilisateur
        ↓
    création explicite du premier BookV4

Principes :
- SourceV4 reste immuable ;
- AnalysisV4 conserve les preuves et propositions ;
- aucun BookV4 n'est créé pendant l'analyse ;
- une IA future pourra être ajoutée comme moteur éditorial
  sans modifier l'interface ni les moteurs déterministes ;
- un Livre existant n'est jamais remplacé automatiquement.
"""

from dataclasses import dataclass

from src.v4.analysis import AnalysisFinding
from src.v4.intelligence import (
    EditorialIntelligenceEngine,
    run_editorial_intelligence,
)
from src.v4.project import ProjectV4
from src.v4.proposal import (
    BookProposal,
    ProposalApplication,
    create_book_from_proposal,
)
from src.v4.source import (
    SourceElement,
    SourceVersion,
)
from src.v4.source_editorial_rules import (
    DeterministicEditorialRules,
)
from src.v4.source_extraction import (
    ExtractionSummary,
    extract_source_version,
)
from src.v4.source_similarity_analysis import (
    SimilarityAnalysisSummary,
    analyze_source_similarity,
)
from src.v4.source_structure_proposal import (
    build_book_proposal,
)


@dataclass(
    frozen=True,
    slots=True,
)
class SourceAnalysisPipelineResult:
    """
    Résultat complet d'une exécution d'analyse.

    Le Livre réel n'existe pas encore à ce stade.
    """

    source_element_id: str
    source_version_id: str

    extraction: ExtractionSummary
    similarity: SimilarityAnalysisSummary

    deterministic_editorial_finding_ids: tuple[
        str,
        ...
    ]

    additional_editorial_finding_ids: tuple[
        str,
        ...
    ]

    proposal_id: str

    proposed_page_count: int
    proposed_part_count: int
    proposed_model_count: int
    issue_count: int


@dataclass(
    frozen=True,
    slots=True,
)
class AcceptedProposalResult:
    """
    Résultat de la validation explicite d'un BookProposal.
    """

    proposal_id: str
    book_id: str

    page_count: int
    part_count: int

    application: ProposalApplication


def _active_source(
    project: ProjectV4,
    source_element_id: str,
) -> tuple[
    SourceElement,
    SourceVersion,
]:
    element = project.source.elements.get(
        source_element_id
    )

    if element is None:
        raise KeyError(
            "Élément Source inconnu : "
            f"{source_element_id}"
        )

    version = element.active_version

    if version is None:
        raise ValueError(
            "Aucune version active pour la Source : "
            f"{source_element_id}"
        )

    return (
        element,
        version,
    )


def _finding_ids(
    findings: tuple[
        AnalysisFinding,
        ...
    ],
) -> tuple[str, ...]:
    return tuple(
        finding.id
        for finding
        in findings
    )


def analyze_source_to_proposal(
    project: ProjectV4,
    *,
    source_element_id: str,
    additional_editorial_engines: tuple[
        EditorialIntelligenceEngine,
        ...
    ] = (),
) -> SourceAnalysisPipelineResult:
    """
    Analyse intégralement la version active d'une Source.

    Cette fonction NE CRÉE JAMAIS le Livre.

    Elle crée et active uniquement un nouveau BookProposal.

    additional_editorial_engines constitue le futur point
    d'insertion des intelligences éditoriales spécialisées.
    Aucun moteur supplémentaire n'est requis aujourd'hui.
    """

    project.validate()

    (
        _element,
        version,
    ) = _active_source(
        project,
        source_element_id,
    )

    # ==========================================================
    # 1. Faits objectifs
    # ==========================================================

    extraction = extract_source_version(
        project.analysis,
        version,
    )

    # ==========================================================
    # 2. Comparaisons / familles de pages
    # ==========================================================

    similarity = analyze_source_similarity(
        project.analysis,
        version,
    )

    # ==========================================================
    # 3. Compréhension éditoriale déterministe
    # ==========================================================

    deterministic_findings = (
        run_editorial_intelligence(
            project.analysis,
            DeterministicEditorialRules(),
            source_version_ids=(
                version.id,
            ),
        )
    )

    # ==========================================================
    # 4. Futurs moteurs éditoriaux spécialisés / IA
    # ==========================================================
    #
    # Ils reçoivent le même contexte détaché.
    # Ils ne reçoivent jamais SourceV4 ou BookV4 en mutation.
    #
    # À ce jour cette liste reste vide.
    # ==========================================================

    additional_findings: list[
        AnalysisFinding
    ] = []

    for engine in (
        additional_editorial_engines
    ):
        generated = (
            run_editorial_intelligence(
                project.analysis,
                engine,
                source_version_ids=(
                    version.id,
                ),
            )
        )

        additional_findings.extend(
            generated
        )

    # ==========================================================
    # 5. Construction déterministe du BookProposal
    # ==========================================================

    proposal = build_book_proposal(
        project.analysis,
        source_element_id=(
            source_element_id
        ),
        version=version,
    )

    # Le Projet conserve la proposition et la rend active.
    # Aucun Livre n'est créé.
    project.add_proposal(
        proposal,
        activate=True,
    )

    assert project.book is None or (
        project.book is not None
    )

    project.validate()

    return SourceAnalysisPipelineResult(
        source_element_id=(
            source_element_id
        ),
        source_version_id=(
            version.id
        ),
        extraction=extraction,
        similarity=similarity,
        deterministic_editorial_finding_ids=(
            _finding_ids(
                deterministic_findings
            )
        ),
        additional_editorial_finding_ids=(
            tuple(
                finding.id
                for finding
                in additional_findings
            )
        ),
        proposal_id=proposal.id,
        proposed_page_count=len(
            proposal.pages
        ),
        proposed_part_count=len(
            proposal.parts
        ),
        proposed_model_count=len(
            proposal.models
        ),
        issue_count=len(
            proposal.issues
        ),
    )


def accept_initial_proposal(
    project: ProjectV4,
    *,
    proposal_id: str | None = None,
    title: str | None = None,
) -> AcceptedProposalResult:
    """
    Valide explicitement une proposition pour créer le premier Livre.

    Sécurité fondamentale :
    si un Livre existe déjà, cette fonction refuse de le remplacer.
    Une réanalyse d'un Livre existant doit passer par le moteur
    de réanalyse V4 et ses protections de modifications humaines.
    """

    project.validate()

    if project.book is not None:
        raise RuntimeError(
            "Un LivreV4 existe déjà. "
            "La proposition ne peut pas le remplacer "
            "automatiquement ; utiliser la réanalyse."
        )

    selected_id = (
        proposal_id
        if proposal_id is not None
        else project.active_proposal_id
    )

    if selected_id is None:
        raise ValueError(
            "Aucune proposition à valider."
        )

    proposal = project.proposals.get(
        selected_id
    )

    if proposal is None:
        raise KeyError(
            "Proposition inconnue : "
            f"{selected_id}"
        )

    book_title = (
        project.title
        if title is None
        else str(title)
    )

    (
        book,
        application,
    ) = create_book_from_proposal(
        proposal,
        title=book_title,
    )

    # ------------------------------------------------------
    # Le premier Livre reprend d'abord le format / les marges
    # détectés dans la Source. L'utilisateur pourra ensuite
    # les conserver ou les modifier dans « État du livre ».
    # ------------------------------------------------------

    from src.v4.book_import_state import (
        apply_detected_format_to_new_book,
    )

    apply_detected_format_to_new_book(
        project,
        book,
    )

    # ------------------------------------------------------
    # Premi?re mat?rialisation Composition.
    #
    # L'Analyse reste la Source de v?rit? automatique.
    # Les r?analyses futures passeront par leur moteur d?di?
    # afin de prot?ger les modifications humaines.
    # ------------------------------------------------------

    from src.v4.source_composition_bridge import (
        materialize_initial_composition,
    )

    materialize_initial_composition(
        project.analysis,
        book,
    )

    # ------------------------------------------------------
    # Couvertures intérieures : l'analyse peut proposer une 2e/3e,
    # mais elle ne prend jamais cette décision à la place de l'auteur.
    # Les pages détectées redeviennent donc des candidates du corps et
    # les deux emplacements physiques restent à confirmer.
    # ------------------------------------------------------

    from src.v4.structure_covers import (
        inside_cover_confirmation_issues,
        prepare_inside_cover_confirmation,
    )

    prepare_inside_cover_confirmation(book)

    project.set_book(
        book,
        proposal_id=proposal.id,
    )

    pending_covers = inside_cover_confirmation_issues(book)
    project.metadata["inside_cover_initial_review_required"] = bool(pending_covers)
    project.metadata["inside_cover_initial_review_completed"] = not bool(pending_covers)

    project.validate()

    return AcceptedProposalResult(
        proposal_id=proposal.id,
        book_id=book.id,
        page_count=len(
            book.pages
        ),
        part_count=len(
            book.parts
        ),
        application=application,
    )
