from __future__ import annotations

"""
Point d'entrée TomeLinea V4 pour la Phase 1 Source.

La Phase 1 analyse et stocke uniquement les faits du DOCX. Elle ne déclenche
ni ressemblance de pages, ni règle éditoriale, ni BookProposal, ni Canvas.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.v4.docx_phase1 import DocxPhase1Result, analyze_docx_phase1
from src.v4.intelligence import record_fact
from src.v4.project import ProjectV4
from src.v4.source_phase1_report import write_phase1_report


ENGINE_NAME = "tomelinea.source_phase1"
ENGINE_VERSION = "2"


@dataclass(frozen=True, slots=True)
class SourcePhase1Result:
    source_element_id: str
    source_version_id: str
    file_type: str
    model: dict[str, Any]
    report_paths: dict[str, str]


def _active_source(project: ProjectV4, source_element_id: str):
    element = project.source.elements.get(source_element_id)
    if element is None:
        raise KeyError(f"Élément Source inconnu : {source_element_id}")
    version = element.active_version
    if version is None:
        raise ValueError(f"Aucune version active pour la Source : {source_element_id}")
    return element, version


def _record(project: ProjectV4, version_id: str, key: str, value: Any) -> None:
    record_fact(
        project.analysis,
        target_type="source_version",
        target_id=version_id,
        key=key,
        value=value,
        engine=ENGINE_NAME,
        engine_version=ENGINE_VERSION,
        source_version_ids=(version_id,),
    )


def analyze_source_phase1(
    project: ProjectV4,
    *,
    source_element_id: str,
    report_dir: str | Path | None = None,
) -> SourcePhase1Result:
    """Analyse uniquement la première phase et s'arrête avant toute édition."""
    project.validate()
    _element, version = _active_source(project, source_element_id)
    file_type = version.file_type.lower().lstrip(".")

    if file_type != "docx":
        raise ValueError(
            "La Phase 1 structurée mise en place ici concerne actuellement le DOCX. "
            f"Format reçu : {file_type or '?'}"
        )

    analyzed: DocxPhase1Result = analyze_docx_phase1(version.original_path)
    model = analyzed.model

    _record(project, version.id, "document.native_kind", "docx_ooxml_structured")
    _record(project, version.id, "document.phase1_schema", model.get("schema"))
    _record(project, version.id, "document.phase1_model", model)
    _record(project, version.id, "document.paragraph_count", model["document"].get("paragraph_count"))
    _record(project, version.id, "document.section_count", model["document"].get("section_count"))
    _record(project, version.id, "document.table_count", model["document"].get("table_count"))
    _record(project, version.id, "document.placed_image_count", model["document"].get("placed_image_count"))
    _record(project, version.id, "document.explicit_page_break_count", model["document"].get("explicit_page_break_count"))
    _record(project, version.id, "document.cached_page_count", model["properties"].get("extended", {}).get("cached_pages"))
    _record(project, version.id, "document.sections", model["document"].get("sections", []))
    _record(project, version.id, "document.font_requirements", model["fonts"].get("face_availability", model["fonts"].get("availability", [])))
    _record(project, version.id, "document.unit_contract", model.get("unit_contract", {}))
    _record(project, version.id, "document.future_editorial_support", model.get("future_editorial_support", {}))

    project.analysis.mark_source_version_analyzed(version.id, version.fingerprint)
    project.analysis.validate()

    if report_dir is None:
        report_dir = Path.cwd() / "diagnostics" / "source_phase1"
    report_paths = write_phase1_report(model, report_dir)

    return SourcePhase1Result(
        source_element_id=source_element_id,
        source_version_id=version.id,
        file_type=file_type,
        model=model,
        report_paths=report_paths,
    )
