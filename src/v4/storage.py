from __future__ import annotations

"""
TomeLinea V4 — persistance du Projet.

Format :
- JSON explicite ;
- schéma identifié ;
- version de stockage indépendante de la version du logiciel ;
- aucune sérialisation Python opaque de type pickle ;
- écriture atomique afin de ne pas détruire une sauvegarde valide
  si l'écriture est interrompue.

Ce module doit pouvoir reconstruire exactement les identités,
baselines, ancres, historiques et décisions humaines.
"""

import json
from pathlib import Path
from typing import Any

from src.v4.analysis import (
    AnalysisFinding,
    AnalysisV4,
    ConfidenceLevel,
    HumanDecision,
)
from src.v4.domain import (
    BookFormat,
    BookKind,
    BookV4,
    PageOrigin,
    PageV4,
    PartV4,
    SourceLink,
)
from src.v4.project import ProjectV4
from src.v4.proposal import (
    BookProposal,
    ProposalIssue,
    ProposedPage,
    ProposedPart,
)
from src.v4.source import (
    SourceElement,
    SourceV4,
    SourceVersion,
)


STORAGE_SCHEMA = "tomelinea-v4-project"
STORAGE_VERSION = 1


# ==============================================================
# Source
# ==============================================================

def _source_link_to_dict(
    value: SourceLink | None,
) -> dict[str, Any] | None:

    if value is None:
        return None

    return {
        "source_id": value.source_id,
        "source_version_id": value.source_version_id,
        "source_page": value.source_page,
    }


def _source_link_from_dict(
    data: dict[str, Any] | None,
) -> SourceLink | None:

    if data is None:
        return None

    return SourceLink(
        source_id=str(data["source_id"]),
        source_version_id=str(
            data["source_version_id"]
        ),
        source_page=data.get(
            "source_page"
        ),
    )


def _source_to_dict(
    source: SourceV4,
) -> dict[str, Any]:

    return {
        "id": source.id,
        "elements": {
            element_id: {
                "id": element.id,
                "active_version_id": (
                    element.active_version_id
                ),
                "versions": [
                    {
                        "id": version.id,
                        "original_name": (
                            version.original_name
                        ),
                        "original_path": (
                            version.original_path
                        ),
                        "file_type": (
                            version.file_type
                        ),
                        "fingerprint": (
                            version.fingerprint
                        ),
                        "size_bytes": (
                            version.size_bytes
                        ),
                        "imported_at": (
                            version.imported_at
                        ),
                    }
                    for version in element.versions
                ],
            }
            for element_id, element
            in source.elements.items()
        },
    }


def _source_from_dict(
    data: dict[str, Any],
) -> SourceV4:

    source = SourceV4(
        id=str(data["id"])
    )

    for element_id, raw in (
        data.get("elements", {}).items()
    ):
        element = SourceElement(
            id=str(raw["id"])
        )

        element.versions = [
            SourceVersion(
                id=str(version["id"]),
                original_name=str(
                    version["original_name"]
                ),
                original_path=str(
                    version["original_path"]
                ),
                file_type=str(
                    version["file_type"]
                ),
                fingerprint=str(
                    version["fingerprint"]
                ),
                size_bytes=int(
                    version["size_bytes"]
                ),
                imported_at=str(
                    version["imported_at"]
                ),
            )
            for version in raw.get(
                "versions",
                [],
            )
        ]

        active = raw.get(
            "active_version_id"
        )

        element.active_version_id = (
            str(active)
            if active is not None
            else None
        )

        source.elements[
            str(element_id)
        ] = element

    source.validate()

    return source


# ==============================================================
# Analyse
# ==============================================================

def _analysis_to_dict(
    analysis: AnalysisV4,
) -> dict[str, Any]:

    return {
        "findings": [
            {
                "id": finding.id,
                "target_type": (
                    finding.target_type
                ),
                "target_id": (
                    finding.target_id
                ),
                "key": finding.key,
                "value": finding.value,
                "confidence": (
                    finding.confidence.value
                ),
                "engine": finding.engine,
                "engine_version": (
                    finding.engine_version
                ),
                "source_version_ids": list(
                    finding.source_version_ids
                ),
                "evidence": list(
                    finding.evidence
                ),
                "created_at": (
                    finding.created_at
                ),
            }
            for finding
            in analysis.findings.values()
        ],

        # Les clés tuple Python sont transformées explicitement
        # en objets JSON.
        "human_decisions": [
            {
                "id": decision.id,
                "target_type": (
                    decision.target_type
                ),
                "target_id": (
                    decision.target_id
                ),
                "key": decision.key,
                "value": decision.value,
                "created_at": (
                    decision.created_at
                ),
            }
            for decision
            in analysis.human_decisions.values()
        ],

        "analyzed_source_versions": dict(
            analysis.analyzed_source_versions
        ),

        "dirty_dependencies": sorted(
            analysis.dirty_dependencies
        ),
    }


def _analysis_from_dict(
    data: dict[str, Any],
) -> AnalysisV4:

    analysis = AnalysisV4()

    for raw in data.get(
        "findings",
        [],
    ):
        finding = AnalysisFinding(
            id=str(raw["id"]),
            target_type=str(
                raw["target_type"]
            ),
            target_id=str(
                raw["target_id"]
            ),
            key=str(raw["key"]),
            value=raw.get("value"),
            confidence=ConfidenceLevel(
                raw["confidence"]
            ),
            engine=str(
                raw["engine"]
            ),
            engine_version=str(
                raw["engine_version"]
            ),
            source_version_ids=tuple(
                str(value)
                for value in raw.get(
                    "source_version_ids",
                    [],
                )
            ),
            evidence=tuple(
                str(value)
                for value in raw.get(
                    "evidence",
                    [],
                )
            ),
            created_at=str(
                raw["created_at"]
            ),
        )

        analysis.findings[
            finding.id
        ] = finding

    for raw in data.get(
        "human_decisions",
        [],
    ):
        decision = HumanDecision(
            id=str(raw["id"]),
            target_type=str(
                raw["target_type"]
            ),
            target_id=str(
                raw["target_id"]
            ),
            key=str(raw["key"]),
            value=raw.get("value"),
            created_at=str(
                raw["created_at"]
            ),
        )

        lookup = (
            decision.target_type,
            decision.target_id,
            decision.key,
        )

        analysis.human_decisions[
            lookup
        ] = decision

    analysis.analyzed_source_versions = {
        str(key): str(value)
        for key, value
        in data.get(
            "analyzed_source_versions",
            {},
        ).items()
    }

    analysis.dirty_dependencies = {
        str(value)
        for value in data.get(
            "dirty_dependencies",
            [],
        )
    }

    analysis.validate()

    return analysis


# ==============================================================
# Propositions
# ==============================================================

def _proposal_to_dict(
    proposal: BookProposal,
) -> dict[str, Any]:

    return {
        "id": proposal.id,
        "created_at": proposal.created_at,
        "suggested_kind": (
            proposal.suggested_kind.value
        ),
        "source_version_ids": list(
            proposal.source_version_ids
        ),

        "parts": [
            {
                "proposal_key": (
                    part.proposal_key
                ),
                "title": part.title,
                "part_type": (
                    part.part_type
                ),
                "parent_key": (
                    part.parent_key
                ),
                "analysis_refs": list(
                    part.analysis_refs
                ),
            }
            for part in proposal.parts
        ],

        "pages": [
            {
                "proposal_key": (
                    page.proposal_key
                ),
                "page_type": (
                    page.page_type
                ),
                "title": page.title,
                "origin": (
                    page.origin.value
                ),
                "source": (
                    _source_link_to_dict(
                        page.source
                    )
                ),
                "part_key": (
                    page.part_key
                ),
                "model_key": (
                    page.model_key
                ),
                "recto_verso": (
                    page.recto_verso
                ),
                "spread_key": (
                    page.spread_key
                ),
                "spread_side": (
                    page.spread_side
                ),
                "is_compensation": (
                    page.is_compensation
                ),
                "analysis_refs": list(
                    page.analysis_refs
                ),
            }
            for page in proposal.pages
        ],

        "models": proposal.models,

        "issues": [
            {
                "code": issue.code,
                "message": issue.message,
                "target_key": (
                    issue.target_key
                ),
                "severity": (
                    issue.severity
                ),
            }
            for issue in proposal.issues
        ],

        "analysis_refs": list(
            proposal.analysis_refs
        ),
    }


def _proposal_from_dict(
    data: dict[str, Any],
) -> BookProposal:

    proposal = BookProposal(
        id=str(data["id"]),
        created_at=str(
            data["created_at"]
        ),
        suggested_kind=BookKind(
            data["suggested_kind"]
        ),
        source_version_ids=tuple(
            str(value)
            for value in data.get(
                "source_version_ids",
                [],
            )
        ),
        models=dict(
            data.get(
                "models",
                {},
            )
        ),
        analysis_refs=tuple(
            str(value)
            for value in data.get(
                "analysis_refs",
                [],
            )
        ),
    )

    for raw in data.get(
        "parts",
        [],
    ):
        proposal.add_part(
            ProposedPart(
                proposal_key=str(
                    raw["proposal_key"]
                ),
                title=str(
                    raw.get(
                        "title",
                        "",
                    )
                ),
                part_type=str(
                    raw.get(
                        "part_type",
                        "partie",
                    )
                ),
                parent_key=(
                    str(raw["parent_key"])
                    if raw.get(
                        "parent_key"
                    ) is not None
                    else None
                ),
                analysis_refs=tuple(
                    str(value)
                    for value in raw.get(
                        "analysis_refs",
                        [],
                    )
                ),
            )
        )

    for raw in data.get(
        "pages",
        [],
    ):
        proposal.add_page(
            ProposedPage(
                proposal_key=str(
                    raw["proposal_key"]
                ),
                page_type=str(
                    raw.get(
                        "page_type",
                        "Page",
                    )
                ),
                title=str(
                    raw.get(
                        "title",
                        "",
                    )
                ),
                origin=PageOrigin(
                    raw.get(
                        "origin",
                        PageOrigin.AUTHOR.value,
                    )
                ),
                source=_source_link_from_dict(
                    raw.get(
                        "source"
                    )
                ),
                part_key=(
                    str(raw["part_key"])
                    if raw.get(
                        "part_key"
                    ) is not None
                    else None
                ),
                model_key=(
                    str(raw["model_key"])
                    if raw.get(
                        "model_key"
                    ) is not None
                    else None
                ),
                recto_verso=raw.get(
                    "recto_verso"
                ),
                spread_key=raw.get(
                    "spread_key"
                ),
                spread_side=raw.get(
                    "spread_side"
                ),
                is_compensation=bool(
                    raw.get(
                        "is_compensation",
                        False,
                    )
                ),
                analysis_refs=tuple(
                    str(value)
                    for value in raw.get(
                        "analysis_refs",
                        [],
                    )
                ),
            )
        )

    proposal.issues = [
        ProposalIssue(
            code=str(raw["code"]),
            message=str(
                raw["message"]
            ),
            target_key=(
                str(raw["target_key"])
                if raw.get(
                    "target_key"
                ) is not None
                else None
            ),
            severity=str(
                raw.get(
                    "severity",
                    "a_verifier",
                )
            ),
        )
        for raw in data.get(
            "issues",
            [],
        )
    ]

    proposal.validate()

    return proposal


# ==============================================================
# Livre
# ==============================================================

def _book_format_to_dict(
    value: BookFormat,
) -> dict[str, Any]:

    return {
        "width_mm": value.width_mm,
        "height_mm": value.height_mm,
        "margin_top_mm": (
            value.margin_top_mm
        ),
        "margin_bottom_mm": (
            value.margin_bottom_mm
        ),
        "margin_inside_mm": (
            value.margin_inside_mm
        ),
        "margin_outside_mm": (
            value.margin_outside_mm
        ),
        "bleed_top_mm": (
            value.bleed_top_mm
        ),
        "bleed_right_mm": (
            value.bleed_right_mm
        ),
        "bleed_bottom_mm": (
            value.bleed_bottom_mm
        ),
        "bleed_left_mm": (
            value.bleed_left_mm
        ),
    }


def _book_format_from_dict(
    data: dict[str, Any],
) -> BookFormat:

    value = BookFormat(
        width_mm=float(
            data["width_mm"]
        ),
        height_mm=float(
            data["height_mm"]
        ),
        margin_top_mm=float(
            data["margin_top_mm"]
        ),
        margin_bottom_mm=float(
            data["margin_bottom_mm"]
        ),
        margin_inside_mm=float(
            data["margin_inside_mm"]
        ),
        margin_outside_mm=float(
            data["margin_outside_mm"]
        ),
        bleed_top_mm=float(
            data["bleed_top_mm"]
        ),
        bleed_right_mm=float(
            data["bleed_right_mm"]
        ),
        bleed_bottom_mm=float(
            data["bleed_bottom_mm"]
        ),
        bleed_left_mm=float(
            data["bleed_left_mm"]
        ),
    )

    value.validate()

    return value


def _book_to_dict(
    book: BookV4,
) -> dict[str, Any]:

    return {
        "id": book.id,
        "title": book.title,
        "kind": book.kind.value,
        "format": (
            _book_format_to_dict(
                book.format
            )
        ),

        "parts": {
            part_id: {
                "id": part.id,
                "title": part.title,
                "part_type": (
                    part.part_type
                ),
                "parent_id": (
                    part.parent_id
                ),
                "metadata": (
                    part.metadata
                ),
                "history": (
                    part.history
                ),
            }
            for part_id, part
            in book.parts.items()
        },

        "part_order": list(
            book.part_order
        ),

        "pages": {
            page_id: {
                "id": page.id,
                "page_type": (
                    page.page_type
                ),
                "title": page.title,
                "origin": (
                    page.origin.value
                ),
                "source": (
                    _source_link_to_dict(
                        page.source
                    )
                ),
                "part_id": (
                    page.part_id
                ),
                "model_id": (
                    page.model_id
                ),
                "recto_verso": (
                    page.recto_verso
                ),
                "spread_id": (
                    page.spread_id
                ),
                "spread_side": (
                    page.spread_side
                ),
                "auto_before": list(
                    page.auto_before
                ),
                "auto_after": list(
                    page.auto_after
                ),
                "is_compensation": (
                    page.is_compensation
                ),
                "content": (
                    page.content
                ),
                "modifications": (
                    page.modifications
                ),
                "history": (
                    page.history
                ),
                "metadata": (
                    page.metadata
                ),
            }
            for page_id, page
            in book.pages.items()
        },

        "page_order": list(
            book.page_order
        ),

        "models": book.models,
        "metadata": book.metadata,
        "history": book.history,
    }


def _book_from_dict(
    data: dict[str, Any],
) -> BookV4:

    book = BookV4(
        id=str(data["id"]),
        title=str(
            data.get(
                "title",
                "",
            )
        ),
        kind=BookKind(
            data["kind"]
        ),
        format=_book_format_from_dict(
            data["format"]
        ),
    )

    # Parties d'abord, afin que les pages puissent ensuite
    # référencer leurs UUID.
    for part_id, raw in (
        data.get(
            "parts",
            {},
        ).items()
    ):
        part = PartV4(
            id=str(raw["id"]),
            title=str(
                raw.get(
                    "title",
                    "",
                )
            ),
            part_type=str(
                raw.get(
                    "part_type",
                    "partie",
                )
            ),
            parent_id=(
                str(raw["parent_id"])
                if raw.get(
                    "parent_id"
                ) is not None
                else None
            ),
            metadata=dict(
                raw.get(
                    "metadata",
                    {},
                )
            ),
            history=list(
                raw.get(
                    "history",
                    [],
                )
            ),
        )

        book.parts[
            str(part_id)
        ] = part

    book.part_order = [
        str(value)
        for value in data.get(
            "part_order",
            [],
        )
    ]

    for page_id, raw in (
        data.get(
            "pages",
            {},
        ).items()
    ):
        page = PageV4(
            id=str(raw["id"]),
            page_type=str(
                raw.get(
                    "page_type",
                    "Page",
                )
            ),
            title=str(
                raw.get(
                    "title",
                    "",
                )
            ),
            origin=PageOrigin(
                raw.get(
                    "origin",
                    PageOrigin.AUTHOR.value,
                )
            ),
            source=_source_link_from_dict(
                raw.get(
                    "source"
                )
            ),
            part_id=(
                str(raw["part_id"])
                if raw.get(
                    "part_id"
                ) is not None
                else None
            ),
            model_id=(
                str(raw["model_id"])
                if raw.get(
                    "model_id"
                ) is not None
                else None
            ),
            recto_verso=raw.get(
                "recto_verso"
            ),
            spread_id=raw.get(
                "spread_id"
            ),
            spread_side=raw.get(
                "spread_side"
            ),
            auto_before=[
                str(value)
                for value in raw.get(
                    "auto_before",
                    [],
                )
            ],
            auto_after=[
                str(value)
                for value in raw.get(
                    "auto_after",
                    [],
                )
            ],
            is_compensation=bool(
                raw.get(
                    "is_compensation",
                    False,
                )
            ),
            content=list(
                raw.get(
                    "content",
                    [],
                )
            ),
            modifications=list(
                raw.get(
                    "modifications",
                    [],
                )
            ),
            history=list(
                raw.get(
                    "history",
                    [],
                )
            ),
            metadata=dict(
                raw.get(
                    "metadata",
                    {},
                )
            ),
        )

        book.pages[
            str(page_id)
        ] = page

    book.page_order = [
        str(value)
        for value in data.get(
            "page_order",
            [],
        )
    ]

    book.models = dict(
        data.get(
            "models",
            {},
        )
    )

    book.metadata = dict(
        data.get(
            "metadata",
            {},
        )
    )

    book.history = list(
        data.get(
            "history",
            [],
        )
    )

    book.validate()

    return book


# ==============================================================
# Projet
# ==============================================================

def project_to_dict(
    project: ProjectV4,
) -> dict[str, Any]:

    project.validate()

    return {
        "schema": STORAGE_SCHEMA,
        "storage_version": STORAGE_VERSION,

        "project": {
            "id": project.id,
            "title": project.title,
            "created_at": (
                project.created_at
            ),
            "updated_at": (
                project.updated_at
            ),

            "source": _source_to_dict(
                project.source
            ),

            "analysis": _analysis_to_dict(
                project.analysis
            ),

            "book": (
                _book_to_dict(
                    project.book
                )
                if project.book is not None
                else None
            ),

            "proposals": {
                proposal_id: (
                    _proposal_to_dict(
                        proposal
                    )
                )
                for proposal_id, proposal
                in project.proposals.items()
            },

            "active_proposal_id": (
                project.active_proposal_id
            ),

            "metadata": (
                project.metadata
            ),

            "history": (
                project.history
            ),
        },
    }


def project_from_dict(
    root: dict[str, Any],
) -> ProjectV4:

    if root.get(
        "schema"
    ) != STORAGE_SCHEMA:
        raise ValueError(
            "Ce fichier n'est pas un projet "
            "TomeLinea V4 reconnu."
        )

    version = root.get(
        "storage_version"
    )

    if version != STORAGE_VERSION:
        raise ValueError(
            "Version de stockage non prise en charge : "
            f"{version}"
        )

    data = root.get(
        "project"
    )

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "Bloc Projet absent ou invalide."
        )

    project = ProjectV4(
        id=str(data["id"]),
        title=str(
            data.get(
                "title",
                "",
            )
        ),
        created_at=str(
            data["created_at"]
        ),
        updated_at=str(
            data["updated_at"]
        ),
        source=_source_from_dict(
            data["source"]
        ),
        analysis=_analysis_from_dict(
            data["analysis"]
        ),
        book=(
            _book_from_dict(
                data["book"]
            )
            if data.get(
                "book"
            ) is not None
            else None
        ),
        active_proposal_id=(
            str(
                data["active_proposal_id"]
            )
            if data.get(
                "active_proposal_id"
            ) is not None
            else None
        ),
        metadata=dict(
            data.get(
                "metadata",
                {},
            )
        ),
        history=list(
            data.get(
                "history",
                [],
            )
        ),
    )

    project.proposals = {
        str(proposal_id): (
            _proposal_from_dict(
                raw
            )
        )
        for proposal_id, raw
        in data.get(
            "proposals",
            {},
        ).items()
    }

    project.validate()

    return project


# ==============================================================
# Fichier
# ==============================================================

def save_project(
    project: ProjectV4,
    path: str | Path,
) -> Path:
    """
    Sauvegarde atomique.

    Le nouveau fichier est écrit à côté du fichier final puis
    remplace celui-ci uniquement lorsque l'écriture est terminée.
    """

    project.validate()

    target = Path(
        path
    ).expanduser().resolve()

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = target.with_name(
        target.name + ".tmp"
    )

    data = project_to_dict(
        project
    )

    try:
        with temporary.open(
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            json.dump(
                data,
                handle,
                ensure_ascii=False,
                indent=2,
                sort_keys=False,
            )

            handle.flush()

        temporary.replace(
            target
        )

    finally:
        if temporary.exists():
            temporary.unlink()

    return target


def load_project(
    path: str | Path,
) -> ProjectV4:

    source = Path(
        path
    ).expanduser().resolve()

    if not source.is_file():
        raise FileNotFoundError(
            source
        )

    with source.open(
        "r",
        encoding="utf-8",
    ) as handle:
        root = json.load(
            handle
        )

    if not isinstance(
        root,
        dict,
    ):
        raise ValueError(
            "Racine de fichier projet invalide."
        )

    return project_from_dict(
        root
    )
