from __future__ import annotations

"""TomeLinea V4 — Phase 2.3 : verrou de chargement Canvas.

Ce module ne dessine rien. Il prépare le document complet pour le moteur Canvas
et garantit que Composition reste invisible tant que le moteur n'a pas confirmé,
dans l'ordre : création du Canvas, chargement des polices, mise en page,
pagination stable puis rendu complet.
"""

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.v4.canvas_contract import CANVAS_SCHEMA, CanvasContractResult, build_canvas_contract
from src.v4.text_quality import TextQualityResult, apply_text_quality_rules
from src.v4.source_phase2 import Phase2Result, analyze_docx_to_phase2

ENGINE_NAME = "tomelinea.canvas_loading"
ENGINE_VERSION = "1"
LOAD_SCHEMA = "tomelinea-canvas-load-session"
LOAD_SCHEMA_VERSION = 1

_REQUIRED_ORDER = (
    "canvas_created",
    "fonts_loaded",
    "layout_complete",
    "pagination_stable",
    "render_complete",
)


class CanvasLoadStateError(RuntimeError):
    pass


@dataclass(slots=True)
class CanvasLoadSession:
    contract: dict[str, Any]
    flags: dict[str, bool] = field(default_factory=lambda: {name: False for name in _REQUIRED_ORDER})
    page_count: int | None = None
    error: dict[str, str] | None = None
    events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.contract.get("schema") != CANVAS_SCHEMA:
            raise ValueError(f"Contrat Canvas inattendu : {self.contract.get('schema')!r}")
        readiness = self.contract.get("readiness", {})
        if not readiness.get("valid_contract"):
            raise ValueError("Contrat Canvas invalide : chargement interdit.")
        if readiness.get("composition_visible"):
            raise ValueError("Le contrat initial ne doit jamais rendre Composition visible.")
        self._record("contract_ready")

    @property
    def failed(self) -> bool:
        return self.error is not None

    @property
    def composition_visible(self) -> bool:
        return (not self.failed) and all(self.flags.values())

    @property
    def stage(self) -> str:
        if self.failed:
            return "failed"
        for name in _REQUIRED_ORDER:
            if not self.flags[name]:
                return name
        return "ready"

    def _record(self, event: str, **details: Any) -> None:
        self.events.append({
            "event": event,
            "composition_visible": self.composition_visible,
            **details,
        })

    def _ensure_not_failed(self) -> None:
        if self.failed:
            raise CanvasLoadStateError("Session Canvas déjà en échec.")

    def _require_previous(self, event: str) -> None:
        index = _REQUIRED_ORDER.index(event)
        missing = [name for name in _REQUIRED_ORDER[:index] if not self.flags[name]]
        if missing:
            raise CanvasLoadStateError(
                f"Étape {event!r} reçue trop tôt ; étapes manquantes : {', '.join(missing)}."
            )

    def _mark(self, event: str, **details: Any) -> None:
        self._ensure_not_failed()
        if event not in self.flags:
            raise ValueError(f"Événement Canvas inconnu : {event}")
        self._require_previous(event)
        if self.flags[event]:
            return
        self.flags[event] = True
        self._record(event, **details)

    def mark_canvas_created(self) -> None:
        self._mark("canvas_created")

    def mark_fonts_loaded(self) -> None:
        self._mark("fonts_loaded")

    def mark_layout_complete(self) -> None:
        self._mark("layout_complete")

    def mark_pagination_stable(self, page_count: int | None = None) -> None:
        if page_count is not None:
            if not isinstance(page_count, int) or page_count < 1:
                raise ValueError("page_count doit être un entier >= 1 quand il est fourni.")
            self.page_count = page_count
        self._mark("pagination_stable", page_count=self.page_count)

    def mark_render_complete(self) -> None:
        self._mark("render_complete")

    def fail(self, stage: str, message: str) -> None:
        if self.failed:
            return
        self.error = {"stage": str(stage), "message": str(message)}
        self._record("failed", stage=str(stage), message=str(message))

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": LOAD_SCHEMA,
            "schema_version": LOAD_SCHEMA_VERSION,
            "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
            "stage": self.stage,
            "flags": dict(self.flags),
            "page_count": self.page_count,
            "failed": self.failed,
            "error": deepcopy(self.error),
            "composition_visible": self.composition_visible,
            "events": deepcopy(self.events),
        }


@dataclass(frozen=True, slots=True)
class CanvasLoadPreparation:
    phase2: Phase2Result
    canvas: CanvasContractResult
    text_quality: TextQualityResult
    session: CanvasLoadSession

    @property
    def ready(self) -> bool:
        return self.phase2.ready_for_canvas and self.canvas.valid and not self.session.failed


def prepare_canvas_load(
    source: str | Path,
    *,
    project_root: str | Path | None = None,
    font_substitutions: dict[str, dict[str, str]] | None = None,
) -> CanvasLoadPreparation:
    """Pipeline complet avant création du widget Canvas.

    1. Analyse Source factuelle (Phase 1, via source_phase2).
    2. Construction du modèle interne Phase 2.
    3. Inventaire des polices Source, sans blocage si elles manquent.
    4. Construction/validation du contrat Canvas.
    5. Création du verrou de visibilité.

    Aucun widget Canvas n'est créé par cette fonction.
    """
    phase2 = analyze_docx_to_phase2(
        source,
        project_root=project_root,
        enforce_font_gate=True,
        font_substitutions=font_substitutions,
    )
    if not phase2.ready_for_canvas:
        raise RuntimeError("Le document interne n'est pas prêt pour Canvas.")

    raw_canvas = build_canvas_contract(phase2.model)
    if not raw_canvas.valid:
        raise RuntimeError("Le contrat Canvas contient des erreurs : " + "; ".join(raw_canvas.errors))

    # L'import garantit d'abord le contenu. Les règles sûres sont analysées
    # maintenant pour pouvoir être proposées globalement lors des réglages, mais
    # elles ne modifient pas silencieusement le contrat importé.
    analyzed_text_quality = apply_text_quality_rules(raw_canvas.contract)
    text_quality = TextQualityResult(
        contract=deepcopy(raw_canvas.contract),
        automatic_corrections=analyzed_text_quality.automatic_corrections,
        editorial_decisions=analyzed_text_quality.editorial_decisions,
        blocking_anomalies=analyzed_text_quality.blocking_anomalies,
    )
    canvas = CanvasContractResult(
        contract=deepcopy(raw_canvas.contract),
        valid=raw_canvas.valid,
        errors=raw_canvas.errors,
    )
    session = CanvasLoadSession(canvas.contract)
    return CanvasLoadPreparation(
        phase2=phase2,
        canvas=canvas,
        text_quality=text_quality,
        session=session,
    )
