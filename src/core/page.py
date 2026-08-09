from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.core.zone import Zone


class Page:
    """
    Représentation complète d'une page éditoriale.

    La page sépare désormais :
    - sa fonction éditoriale ;
    - sa nature de travail ;
    - sa géométrie d'impression ;
    - son fond ;
    - ses zones polyvalentes ;
    - les espaces autorisés à modifier sa structure ou son contenu.
    """

    VERSION = "3.0"

    DEFAULT_TYPE = "Page vide"
    DEFAULT_STATE = "Brouillon"
    DEFAULT_COLOR = "#D9D4C7"
    DEFAULT_ICON = "📄"

    DEFAULT_FORMAT = "A5"
    DEFAULT_ORIENTATION = "Portrait"
    DEFAULT_KIND = "page_unique"

    FORMAT_PRESETS: dict[str, tuple[float, float]] = {
        "A3": (297.0, 420.0),
        "A4": (210.0, 297.0),
        "A5": (148.0, 210.0),
        "A6": (105.0, 148.0),
        "16 × 24 cm": (160.0, 240.0),
        "Carré 210": (210.0, 210.0),
        "Lettre": (215.9, 279.4),
    }

    ORIENTATIONS = {
        "Portrait",
        "Paysage",
    }

    PAGE_KINDS = {
        "page_unique",
        "modele",
        "page_produite",
        "page_textuelle",
    }

    WORKSPACES = {
        "atelier",
        "production",
        "composition",
        "centre",
        "finalisation",
    }

    BACKGROUND_SCOPES = {
        "page",
        "surface_composition",
        "fonds_perdus",
    }

    BACKGROUND_FIT_MODES = {
        "remplir",
        "ajuster",
        "manuel",
    }

    def __init__(self) -> None:
        # Identité
        self.identifier = str(uuid4())
        self.number = 1
        self.title = ""
        self.page_type = self.DEFAULT_TYPE

        # État éditorial
        self.state = self.DEFAULT_STATE
        self.color = self.DEFAULT_COLOR
        self.icon = self.DEFAULT_ICON
        self.locked = False

        # Nature fonctionnelle
        self.page_kind = self.DEFAULT_KIND
        self.structure_workspace = "atelier"
        self.content_workspace = "atelier"

        # Sources éventuelles
        self.source_model_id = ""
        self.source_model_version = ""
        self.source_content_id = ""

        # LIEN_STABLE_MAQUETTAGE_CONCEPTION_V1
        # Référence de la page logique prévue au Maquettage.
        self.source_mockup_item_id = ""
        self.source_mockup_occurrence = 1

        # Informations
        self.author = ""
        self.description = ""
        self.tags: list[str] = []

        # Format physique
        self.format = self.DEFAULT_FORMAT
        self.format_mode = "preregle"
        self.orientation = self.DEFAULT_ORIENTATION
        self.width_mm = 148.0
        self.height_mm = 210.0

        # Marges de composition
        self.margin_top_mm = 15.0
        self.margin_bottom_mm = 15.0
        self.margin_inside_mm = 15.0
        self.margin_outside_mm = 15.0

        # Fonds perdus
        self.bleed_top_mm = 0.0
        self.bleed_right_mm = 0.0
        self.bleed_bottom_mm = 0.0
        self.bleed_left_mm = 0.0

        # Fond structurel de page
        self.background = self._default_background()

        # Contenu général
        self.content: dict[str, Any] = {}

        # Tous les objets éditoriaux sont conservés ici.
        # Les zones polyvalentes utilisent type == Zone.ELEMENT_TYPE.
        self.elements: list[dict[str, Any]] = []

        # Historique
        self.history: list[dict[str, str]] = []

        # Dates
        self.created = ""
        self.modified = ""

        # Emplacement
        self.root: Path | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def is_loaded(self) -> bool:
        return self.root is not None

    @property
    def display_title(self) -> str:
        return self.title or f"Page {self.number:03d}"

    @property
    def folder_name(self) -> str:
        return f"page_{self.number:04d}"

    @property
    def page_size_mm(self) -> tuple[float, float]:
        return (
            self.width_mm,
            self.height_mm,
        )

    @property
    def page_size_with_bleed_mm(self) -> tuple[float, float]:
        return (
            self.width_mm + self.bleed_left_mm + self.bleed_right_mm,
            self.height_mm + self.bleed_top_mm + self.bleed_bottom_mm,
        )

    @property
    def zone_count(self) -> int:
        return len(self.get_zones())

    @property
    def has_background(self) -> bool:
        return bool(
            self.background.get("active")
            and self.background.get("ressource")
        )

    def set_mockup_source(
        self,
        item_id: str,
        occurrence: int = 1,
    ) -> None:
        # Associe cette page à une occurrence précise du Maquettage.
        self.source_mockup_item_id = str(item_id or "").strip()

        try:
            self.source_mockup_occurrence = max(1, int(occurrence))
        except (TypeError, ValueError):
            self.source_mockup_occurrence = 1

    # ==========================================================
    # Création
    # ==========================================================

    def create(
        self,
        pages_folder: str | Path,
        number: int,
        page_type: str | None = None,
        title: str | None = None,
    ) -> Path:
        self.number = number

        if page_type:
            self.page_type = page_type

        if title:
            self.title = title.strip()

        now = datetime.now().isoformat()

        self.created = now
        self.modified = now

        self.root = Path(pages_folder) / self.folder_name

        self._require_root().mkdir(
            parents=True,
            exist_ok=True,
        )

        self._add_history(
            action="creation",
            description="Création de la page.",
        )

        self.save(
            update_history=False,
        )

        return self._require_root()

    # ==========================================================
    # Chargement
    # ==========================================================

    def load(
        self,
        folder: str | Path,
    ) -> Page:
        self.root = Path(folder)

        page_file = self._require_root() / "page.json"

        with page_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        identity = data.get(
            "identite",
            {},
        )

        editorial = data.get(
            "editorial",
            {},
        )

        workflow = data.get(
            "fonctionnement",
            {},
        )

        metadata = data.get(
            "metadonnees",
            {},
        )

        layout = data.get(
            "mise_en_page",
            {},
        )

        # Identité
        self.identifier = identity.get(
            "identifiant",
            str(uuid4()),
        )

        self.number = self._safe_int(
            identity.get("numero", 1),
            default=1,
        )

        self.title = str(
            identity.get(
                "nom",
                "",
            )
        )

        self.page_type = str(
            identity.get(
                "type",
                self.DEFAULT_TYPE,
            )
        )

        # Compatibilité avec les anciennes pages
        self.state = str(
            editorial.get(
                "etat",
                identity.get(
                    "etat",
                    self.DEFAULT_STATE,
                ),
            )
        )

        self.color = str(
            editorial.get(
                "couleur",
                self.DEFAULT_COLOR,
            )
        )

        self.icon = str(
            editorial.get(
                "icone",
                self.DEFAULT_ICON,
            )
        )

        self.locked = bool(
            editorial.get(
                "verrouillee",
                False,
            )
        )

        # Nature fonctionnelle et espaces de modification
        self.page_kind = self._normalize_page_kind(
            workflow.get(
                "nature",
                self.DEFAULT_KIND,
            )
        )

        default_structure_workspace, default_content_workspace = (
            self._default_workspaces_for_kind(self.page_kind)
        )

        self.structure_workspace = self._normalize_workspace(
            workflow.get(
                "espace_structure",
                default_structure_workspace,
            ),
            allow_empty=True,
        )

        self.content_workspace = self._normalize_workspace(
            workflow.get(
                "espace_contenu",
                default_content_workspace,
            ),
            allow_empty=True,
        )

        sources = workflow.get(
            "sources",
            {},
        )

        self.source_model_id = str(
            sources.get(
                "modele",
                "",
            )
        )

        self.source_model_version = str(
            sources.get(
                "version_modele",
                "",
            )
        )

        self.source_content_id = str(
            sources.get(
                "contenu",
                "",
            )
        )

        self.source_mockup_item_id = str(
            sources.get(
                "maquettage_item",
                "",
            )
        ).strip()

        try:
            self.source_mockup_occurrence = max(
                1,
                int(sources.get("maquettage_occurrence", 1)),
            )
        except (TypeError, ValueError):
            self.source_mockup_occurrence = 1

        # Métadonnées
        self.author = str(
            metadata.get(
                "auteur",
                "",
            )
        )

        self.created = str(
            metadata.get(
                "creation",
                "",
            )
        )

        self.modified = str(
            metadata.get(
                "modification",
                "",
            )
        )

        self.description = str(
            metadata.get(
                "description",
                "",
            )
        )

        self.tags = [
            str(tag)
            for tag in metadata.get(
                "mots_cles",
                [],
            )
        ]

        # Mise en page
        self._load_layout(layout)

        # Contenu
        self.content = dict(
            data.get(
                "contenu",
                {},
            )
        )

        self.elements = [
            dict(element)
            for element in data.get(
                "elements",
                [],
            )
            if isinstance(element, dict)
        ]

        self.history = [
            dict(entry)
            for entry in data.get(
                "historique",
                [],
            )
            if isinstance(entry, dict)
        ]

        return self

    # ==========================================================
    # Modification éditoriale
    # ==========================================================

    def rename(
        self,
        title: str,
    ) -> None:
        self._ensure_editable()

        new_title = title.strip()

        if new_title == self.title:
            return

        old_title = self.display_title
        self.title = new_title

        self._add_history(
            action="renommage",
            description=(
                f"Renommage de « {old_title} » "
                f"en « {self.display_title} »."
            ),
        )

        self.save(
            update_history=False,
        )

    def set_type(
        self,
        page_type: str,
    ) -> None:
        self._ensure_editable()

        page_type = page_type.strip() or self.DEFAULT_TYPE

        if page_type == self.page_type:
            return

        previous_type = self.page_type
        self.page_type = page_type

        self._add_history(
            action="changement_type",
            description=(
                f"Type modifié de « {previous_type} » "
                f"vers « {page_type} »."
            ),
        )

        self.save(
            update_history=False,
        )

    def set_state(
        self,
        state: str,
    ) -> None:
        state = state.strip() or self.DEFAULT_STATE

        if state == self.state:
            return

        previous_state = self.state
        self.state = state

        self._add_history(
            action="changement_etat",
            description=(
                f"État modifié de « {previous_state} » "
                f"vers « {state} »."
            ),
        )

        self.save(
            update_history=False,
        )

    def set_locked(
        self,
        locked: bool,
    ) -> None:
        locked = bool(locked)

        if locked == self.locked:
            return

        self.locked = locked

        self._add_history(
            action="verrouillage" if locked else "deverrouillage",
            description=(
                "Page verrouillée."
                if locked
                else "Page déverrouillée."
            ),
        )

        self.save(
            update_history=False,
        )

    def set_description(
        self,
        description: str,
    ) -> None:
        self._ensure_editable()

        self.description = description.strip()

        self._add_history(
            action="description",
            description="Description de la page modifiée.",
        )

        self.save(
            update_history=False,
        )

    def set_content(
        self,
        content: dict,
    ) -> None:
        self._ensure_editable()

        self.content = dict(content)

        self._add_history(
            action="contenu",
            description="Contenu de la page modifié.",
        )

        self.save(
            update_history=False,
        )

    # ==========================================================
    # Nature de la page et verrouillage par espace
    # ==========================================================

    def set_page_kind(
        self,
        page_kind: str,
    ) -> None:
        self._ensure_editable()

        normalized_kind = self._normalize_page_kind(page_kind)

        if normalized_kind == self.page_kind:
            return

        previous_kind = self.page_kind
        self.page_kind = normalized_kind

        (
            self.structure_workspace,
            self.content_workspace,
        ) = self._default_workspaces_for_kind(normalized_kind)

        self._add_history(
            action="changement_nature",
            description=(
                f"Nature de page modifiée de « {previous_kind} » "
                f"vers « {normalized_kind} »."
            ),
        )

        self.save(
            update_history=False,
        )

    def set_source_links(
        self,
        *,
        model_id: str = "",
        model_version: str = "",
        content_id: str = "",
    ) -> None:
        self.source_model_id = model_id.strip()
        self.source_model_version = model_version.strip()
        self.source_content_id = content_id.strip()

        self._add_history(
            action="liaison_sources",
            description="Sources de la page mises à jour.",
        )

        self.save(
            update_history=False,
        )

    def can_edit_structure(
        self,
        workspace: str,
    ) -> bool:
        if self.locked:
            return False

        normalized_workspace = self._normalize_workspace(workspace)

        return bool(
            self.structure_workspace
            and normalized_workspace == self.structure_workspace
        )

    def can_edit_content(
        self,
        workspace: str,
    ) -> bool:
        if self.locked:
            return False

        normalized_workspace = self._normalize_workspace(workspace)

        return bool(
            self.content_workspace
            and normalized_workspace == self.content_workspace
        )

    def can_edit(
        self,
        workspace: str,
        scope: str = "structure",
    ) -> bool:
        normalized_scope = scope.strip().lower()

        if normalized_scope == "structure":
            return self.can_edit_structure(workspace)

        if normalized_scope == "contenu":
            return self.can_edit_content(workspace)

        raise ValueError(
            "La portée doit être « structure » ou « contenu »."
        )

    # ==========================================================
    # Format, marges et fonds perdus
    # ==========================================================

    def set_format(
        self,
        format_name: str,
        orientation: str | None = None,
    ) -> None:
        self._ensure_editable()

        normalized_name = format_name.strip()

        if normalized_name not in self.FORMAT_PRESETS:
            raise ValueError(
                f"Format prédéfini inconnu : {normalized_name}"
            )

        normalized_orientation = self._normalize_orientation(
            orientation or self.orientation
        )

        base_width, base_height = self.FORMAT_PRESETS[normalized_name]
        width, height = self._oriented_size(
            base_width,
            base_height,
            normalized_orientation,
        )

        self.format = normalized_name
        self.format_mode = "preregle"
        self.orientation = normalized_orientation
        self.width_mm = width
        self.height_mm = height

        self._reset_background_frame_if_automatic()

        self._add_history(
            action="format_page",
            description=(
                f"Format de page défini sur « {normalized_name} » "
                f"en orientation « {normalized_orientation} »."
            ),
        )

        self.save(
            update_history=False,
        )

    def set_custom_format(
        self,
        width_mm: float,
        height_mm: float,
        orientation: str = DEFAULT_ORIENTATION,
        label: str = "Format libre",
    ) -> None:
        self._ensure_editable()

        width = self._validate_positive_number(
            width_mm,
            "largeur de page",
        )

        height = self._validate_positive_number(
            height_mm,
            "hauteur de page",
        )

        normalized_orientation = self._normalize_orientation(
            orientation
        )

        width, height = self._oriented_size(
            width,
            height,
            normalized_orientation,
        )

        self.format = label.strip() or "Format libre"
        self.format_mode = "libre"
        self.orientation = normalized_orientation
        self.width_mm = width
        self.height_mm = height

        self._reset_background_frame_if_automatic()

        self._add_history(
            action="format_page_libre",
            description=(
                f"Format libre défini sur "
                f"{width:.2f} × {height:.2f} mm."
            ),
        )

        self.save(
            update_history=False,
        )

    def set_orientation(
        self,
        orientation: str,
    ) -> None:
        self._ensure_editable()

        normalized_orientation = self._normalize_orientation(
            orientation
        )

        if normalized_orientation == self.orientation:
            return

        self.orientation = normalized_orientation
        self.width_mm, self.height_mm = (
            self.height_mm,
            self.width_mm,
        )

        self._reset_background_frame_if_automatic()

        self._add_history(
            action="orientation_page",
            description=(
                f"Orientation définie sur « {normalized_orientation} »."
            ),
        )

        self.save(
            update_history=False,
        )

    def set_margins(
        self,
        *,
        top_mm: float,
        bottom_mm: float,
        inside_mm: float,
        outside_mm: float,
    ) -> None:
        self._ensure_editable()

        margins = {
            "haut": self._validate_non_negative_number(
                top_mm,
                "marge haute",
            ),
            "bas": self._validate_non_negative_number(
                bottom_mm,
                "marge basse",
            ),
            "interieure": self._validate_non_negative_number(
                inside_mm,
                "marge intérieure",
            ),
            "exterieure": self._validate_non_negative_number(
                outside_mm,
                "marge extérieure",
            ),
        }

        if margins["haut"] + margins["bas"] >= self.height_mm:
            raise ValueError(
                "Les marges haute et basse occupent toute la hauteur."
            )

        if (
            margins["interieure"] + margins["exterieure"]
            >= self.width_mm
        ):
            raise ValueError(
                "Les marges intérieure et extérieure "
                "occupent toute la largeur."
            )

        self.margin_top_mm = margins["haut"]
        self.margin_bottom_mm = margins["bas"]
        self.margin_inside_mm = margins["interieure"]
        self.margin_outside_mm = margins["exterieure"]

        self._add_history(
            action="marges_page",
            description="Marges de composition modifiées.",
        )

        self.save(
            update_history=False,
        )

    def set_bleed(
        self,
        *,
        top_mm: float,
        right_mm: float,
        bottom_mm: float,
        left_mm: float,
    ) -> None:
        self._ensure_editable()

        self.bleed_top_mm = self._validate_non_negative_number(
            top_mm,
            "fond perdu haut",
        )
        self.bleed_right_mm = self._validate_non_negative_number(
            right_mm,
            "fond perdu droit",
        )
        self.bleed_bottom_mm = self._validate_non_negative_number(
            bottom_mm,
            "fond perdu bas",
        )
        self.bleed_left_mm = self._validate_non_negative_number(
            left_mm,
            "fond perdu gauche",
        )

        self._add_history(
            action="fonds_perdus",
            description="Fonds perdus modifiés.",
        )

        self.save(
            update_history=False,
        )

    def composition_box_mm(
        self,
        *,
        verso: bool = False,
    ) -> dict[str, float]:
        if verso:
            left = self.margin_outside_mm
            right = self.margin_inside_mm
        else:
            left = self.margin_inside_mm
            right = self.margin_outside_mm

        return {
            "x": left,
            "y": self.margin_top_mm,
            "largeur": self.width_mm - left - right,
            "hauteur": (
                self.height_mm
                - self.margin_top_mm
                - self.margin_bottom_mm
            ),
        }

    # ==========================================================
    # Image de fond
    # ==========================================================

    def set_background(
        self,
        resource: str,
        *,
        scope: str = "page",
        fit_mode: str = "remplir",
        keep_aspect_ratio: bool = True,
        opacity: float = 1.0,
    ) -> None:
        self._ensure_editable()

        normalized_scope = self._normalize_background_scope(scope)
        normalized_fit_mode = self._normalize_background_fit_mode(
            fit_mode
        )
        opacity_value = self._validate_opacity(opacity)

        target = self._background_target_box(normalized_scope)

        self.background = {
            "nature": "fixe",
            "active": True,
            "ressource": resource.strip(),
            "portee": normalized_scope,
            "mode": normalized_fit_mode,
            "conserver_proportions": bool(keep_aspect_ratio),
            "opacite": opacity_value,
            "cadre_automatique": normalized_fit_mode != "manuel",
            "x_mm": target["x"],
            "y_mm": target["y"],
            "largeur_mm": target["largeur"],
            "hauteur_mm": target["hauteur"],
            "rotation": 0.0,
        }

        self._add_history(
            action="fond_page",
            description="Image de fond définie.",
        )

        self.save(
            update_history=False,
        )

    def set_variable_background(
        self,
        *,
        scope: str = "page",
        fit_mode: str = "remplir",
        keep_aspect_ratio: bool = True,
    ) -> None:
        """Déclare un emplacement de fond variable pour la Production."""

        self._ensure_editable()

        normalized_scope = self._normalize_background_scope(scope)
        normalized_fit_mode = self._normalize_background_fit_mode(
            fit_mode
        )
        target = self._background_target_box(normalized_scope)

        self.background = {
            "nature": "variable",
            "active": False,
            "ressource": "",
            "portee": normalized_scope,
            "mode": normalized_fit_mode,
            "conserver_proportions": bool(keep_aspect_ratio),
            "opacite": 1.0,
            "cadre_automatique": True,
            "x_mm": target["x"],
            "y_mm": target["y"],
            "largeur_mm": target["largeur"],
            "hauteur_mm": target["hauteur"],
            "rotation": 0.0,
        }

        self._add_history(
            action="fond_variable",
            description="Emplacement de fond variable défini.",
        )

        self.save(
            update_history=False,
        )

    def set_background_transform(
        self,
        *,
        x_mm: float | None = None,
        y_mm: float | None = None,
        width_mm: float | None = None,
        height_mm: float | None = None,
        rotation: float | None = None,
        keep_aspect_ratio: bool | None = None,
    ) -> None:
        self._ensure_editable()

        if not self.background.get("active"):
            raise RuntimeError(
                "Aucune image de fond n'est actuellement définie."
            )

        self.background["mode"] = "manuel"
        self.background["cadre_automatique"] = False

        if x_mm is not None:
            self.background["x_mm"] = self._validate_number(
                x_mm,
                "position horizontale du fond",
            )

        if y_mm is not None:
            self.background["y_mm"] = self._validate_number(
                y_mm,
                "position verticale du fond",
            )

        if width_mm is not None:
            self.background["largeur_mm"] = (
                self._validate_positive_number(
                    width_mm,
                    "largeur du fond",
                )
            )

        if height_mm is not None:
            self.background["hauteur_mm"] = (
                self._validate_positive_number(
                    height_mm,
                    "hauteur du fond",
                )
            )

        if rotation is not None:
            self.background["rotation"] = (
                self._normalize_rotation(rotation)
            )

        if keep_aspect_ratio is not None:
            self.background["conserver_proportions"] = bool(
                keep_aspect_ratio
            )

        self._add_history(
            action="cadrage_fond",
            description="Cadrage manuel de l'image de fond modifié.",
        )

        self.save(
            update_history=False,
        )

    def reset_background_frame(self) -> None:
        self._ensure_editable()

        if not self.background.get("active"):
            return

        scope = self._normalize_background_scope(
            self.background.get(
                "portee",
                "page",
            )
        )

        target = self._background_target_box(scope)

        self.background.update(
            {
                "mode": "remplir",
                "cadre_automatique": True,
                "x_mm": target["x"],
                "y_mm": target["y"],
                "largeur_mm": target["largeur"],
                "hauteur_mm": target["hauteur"],
                "rotation": 0.0,
            }
        )

        self._add_history(
            action="reinitialisation_fond",
            description="Cadrage automatique du fond restauré.",
        )

        self.save(
            update_history=False,
        )

    def clear_background(self) -> None:
        self._ensure_editable()

        if (
            not self.background.get("active")
            and self.background.get("nature", "aucun") == "aucun"
        ):
            return

        self.background = self._default_background()

        self._add_history(
            action="suppression_fond",
            description="Image de fond supprimée.",
        )

        self.save(
            update_history=False,
        )

    # ==========================================================
    # Éléments généraux
    # ==========================================================

    def get_elements_by_type(
        self,
        element_type: str,
    ) -> list[dict]:
        """
        Retourne une copie des éléments correspondant au type demandé.
        """
        return [
            deepcopy(element)
            for element in self.elements
            if element.get("type") == element_type
        ]

    def replace_elements_by_type(
        self,
        element_type: str,
        elements: list[dict],
        save: bool = True,
    ) -> None:
        """
        Remplace tous les éléments d'un type sans toucher aux autres.
        """
        self._ensure_editable()

        preserved_elements = [
            element
            for element in self.elements
            if element.get("type") != element_type
        ]

        normalized_elements = []

        for element in elements:
            normalized_element = deepcopy(element)
            normalized_element["type"] = element_type
            normalized_elements.append(normalized_element)

        self.elements = preserved_elements + normalized_elements

        if save:
            self.save(
                update_history=False,
            )

    # ==========================================================
    # Zones polyvalentes
    # ==========================================================

    def get_zones(self) -> list[Zone]:
        zones: list[Zone] = []

        for element in self.elements:
            if element.get("type") != Zone.ELEMENT_TYPE:
                continue

            try:
                zones.append(
                    Zone.from_dict(element)
                )
            except (TypeError, ValueError):
                continue

        return zones

    def get_zone(
        self,
        identifier: str,
    ) -> Zone | None:
        for zone in self.get_zones():
            if zone.identifier == identifier:
                return zone

        return None

    def add_zone(
        self,
        zone: Zone,
        *,
        save: bool = True,
    ) -> None:
        self._ensure_editable()

        if not isinstance(zone, Zone):
            raise TypeError(
                "L'élément ajouté doit être une instance de Zone."
            )

        if self.get_zone(zone.identifier) is not None:
            raise ValueError(
                "Une zone portant cet identifiant existe déjà."
            )

        self.elements.append(
            zone.to_dict()
        )

        self._add_history(
            action="ajout_zone",
            description=f"Ajout de « {zone.display_name} ».",
        )

        if save:
            self.save(
                update_history=False,
            )

    def update_zone(
        self,
        zone: Zone,
        *,
        save: bool = True,
    ) -> None:
        self._ensure_editable()

        if not isinstance(zone, Zone):
            raise TypeError(
                "L'élément mis à jour doit être une instance de Zone."
            )

        for index, element in enumerate(self.elements):
            if (
                element.get("type") == Zone.ELEMENT_TYPE
                and element.get(
                    "identite",
                    {},
                ).get("identifiant") == zone.identifier
            ):
                self.elements[index] = zone.to_dict()

                self._add_history(
                    action="modification_zone",
                    description=(
                        f"Modification de « {zone.display_name} »."
                    ),
                )

                if save:
                    self.save(
                        update_history=False,
                    )

                return

        raise KeyError(
            f"Zone introuvable : {zone.identifier}"
        )

    def remove_zone(
        self,
        identifier: str,
        *,
        save: bool = True,
    ) -> Zone | None:
        self._ensure_editable()

        for index, element in enumerate(self.elements):
            if element.get("type") != Zone.ELEMENT_TYPE:
                continue

            element_id = element.get(
                "identite",
                {},
            ).get("identifiant")

            if element_id != identifier:
                continue

            removed = Zone.from_dict(
                self.elements.pop(index)
            )

            self._add_history(
                action="suppression_zone",
                description=(
                    f"Suppression de « {removed.display_name} »."
                ),
            )

            if save:
                self.save(
                    update_history=False,
                )

            return removed

        return None

    def duplicate_zone(
        self,
        identifier: str,
        *,
        offset_x: float = 5.0,
        offset_y: float = 5.0,
        save: bool = True,
    ) -> Zone | None:
        self._ensure_editable()

        source = self.get_zone(identifier)

        if source is None:
            return None

        duplicate = source.clone(
            keep_content=True,
        )
        duplicate.move(
            offset_x,
            offset_y,
        )

        self.elements.append(
            duplicate.to_dict()
        )

        self._add_history(
            action="duplication_zone",
            description=(
                f"Duplication de « {source.display_name} »."
            ),
        )

        if save:
            self.save(
                update_history=False,
            )

        return duplicate

    # ==========================================================
    # Sauvegarde
    # ==========================================================

    def save(
        self,
        update_history: bool = True,
    ) -> None:
        if not self.is_loaded:
            return

        self.modified = datetime.now().isoformat()

        if update_history:
            self._add_history(
                action="sauvegarde",
                description="Sauvegarde de la page.",
            )

        page_file = self._require_root() / "page.json"

        with page_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.to_dict(),
                file,
                indent=4,
                ensure_ascii=False,
            )

    # ==========================================================
    # Données
    # ==========================================================

    def to_summary(self) -> dict:
        """
        Informations légères enregistrées dans document.json.
        """
        return {
            "identifiant": self.identifier,
            "numero": self.number,
            "nom": self.display_title,
            "type": self.page_type,
            "nature": self.page_kind,
            "etat": self.state,
            "couleur": self.color,
            "icone": self.icon,
            "verrouillee": self.locked,
            "dossier": self.folder_name,
            "source_modele": self.source_model_id,
            "source_maquettage_id": self.source_mockup_item_id,
            "source_maquettage_occurrence": self.source_mockup_occurrence,
            "date_creation": self.created,
            "date_modification": self.modified,
        }

    def to_dict(self) -> dict:
        return {
            "identite": {
                "identifiant": self.identifier,
                "numero": self.number,
                "nom": self.display_title,
                "type": self.page_type,
                "version": self.VERSION,
            },
            "editorial": {
                "etat": self.state,
                "couleur": self.color,
                "icone": self.icon,
                "verrouillee": self.locked,
            },
            "fonctionnement": {
                "nature": self.page_kind,
                "espace_structure": self.structure_workspace,
                "espace_contenu": self.content_workspace,
                "sources": {
                    "modele": self.source_model_id,
                    "version_modele": self.source_model_version,
                    "contenu": self.source_content_id,
                    "maquettage_item": self.source_mockup_item_id,
                    "maquettage_occurrence": self.source_mockup_occurrence,
                },
            },
            "metadonnees": {
                "auteur": self.author,
                "creation": self.created,
                "modification": self.modified,
                "description": self.description,
                "mots_cles": self.tags,
            },
            "mise_en_page": {
                "format": self.format,
                "mode_format": self.format_mode,
                "orientation": self.orientation,
                "largeur_mm": self.width_mm,
                "hauteur_mm": self.height_mm,
                "marges_mm": {
                    "haut": self.margin_top_mm,
                    "bas": self.margin_bottom_mm,
                    "interieure": self.margin_inside_mm,
                    "exterieure": self.margin_outside_mm,
                },
                "fonds_perdus_mm": {
                    "haut": self.bleed_top_mm,
                    "droite": self.bleed_right_mm,
                    "bas": self.bleed_bottom_mm,
                    "gauche": self.bleed_left_mm,
                },
                "fond": deepcopy(self.background),
            },
            "contenu": deepcopy(self.content),
            "elements": deepcopy(self.elements),
            "historique": deepcopy(self.history),
        }

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self) -> list[str]:
        errors: list[str] = []

        if self.width_mm <= 0:
            errors.append(
                "La largeur de page doit être supérieure à zéro."
            )

        if self.height_mm <= 0:
            errors.append(
                "La hauteur de page doit être supérieure à zéro."
            )

        if (
            self.margin_top_mm + self.margin_bottom_mm
            >= self.height_mm
        ):
            errors.append(
                "Les marges verticales occupent toute la page."
            )

        if (
            self.margin_inside_mm + self.margin_outside_mm
            >= self.width_mm
        ):
            errors.append(
                "Les marges horizontales occupent toute la page."
            )

        if self.page_kind == "page_produite":
            if not self.source_model_id:
                errors.append(
                    "Une page produite doit référencer son modèle."
                )

        if self.has_background:
            if self.background.get("largeur_mm", 0.0) <= 0:
                errors.append(
                    "La largeur de l'image de fond est invalide."
                )

            if self.background.get("hauteur_mm", 0.0) <= 0:
                errors.append(
                    "La hauteur de l'image de fond est invalide."
                )

        for zone in self.get_zones():
            errors.extend(
                f"{zone.display_name} : {error}"
                for error in zone.validate()
            )

        return errors

    # ==========================================================
    # Historique
    # ==========================================================

    def _add_history(
        self,
        action: str,
        description: str,
    ) -> None:
        self.history.append(
            {
                "date": datetime.now().isoformat(),
                "action": action,
                "description": description,
            }
        )

    # ==========================================================
    # Chargement de la mise en page
    # ==========================================================

    def _load_layout(
        self,
        layout: dict,
    ) -> None:
        format_name = str(
            layout.get(
                "format",
                self.DEFAULT_FORMAT,
            )
        )

        orientation = self._normalize_orientation(
            layout.get(
                "orientation",
                self.DEFAULT_ORIENTATION,
            )
        )

        format_mode = str(
            layout.get(
                "mode_format",
                "preregle",
            )
        ).strip().lower()

        if format_mode not in {"preregle", "libre"}:
            format_mode = "preregle"

        default_width, default_height = self.FORMAT_PRESETS.get(
            format_name,
            self.FORMAT_PRESETS[self.DEFAULT_FORMAT],
        )

        default_width, default_height = self._oriented_size(
            default_width,
            default_height,
            orientation,
        )

        self.format = format_name
        self.format_mode = format_mode
        self.orientation = orientation
        self.width_mm = self._safe_positive_number(
            layout.get(
                "largeur_mm",
                default_width,
            ),
            default=default_width,
        )
        self.height_mm = self._safe_positive_number(
            layout.get(
                "hauteur_mm",
                default_height,
            ),
            default=default_height,
        )

        margins = layout.get(
            "marges_mm",
            {},
        )

        self.margin_top_mm = self._safe_non_negative_number(
            margins.get(
                "haut",
                15.0,
            ),
            default=15.0,
        )
        self.margin_bottom_mm = self._safe_non_negative_number(
            margins.get(
                "bas",
                15.0,
            ),
            default=15.0,
        )
        self.margin_inside_mm = self._safe_non_negative_number(
            margins.get(
                "interieure",
                15.0,
            ),
            default=15.0,
        )
        self.margin_outside_mm = self._safe_non_negative_number(
            margins.get(
                "exterieure",
                15.0,
            ),
            default=15.0,
        )

        bleed = layout.get(
            "fonds_perdus_mm",
            {},
        )

        self.bleed_top_mm = self._safe_non_negative_number(
            bleed.get(
                "haut",
                0.0,
            ),
            default=0.0,
        )
        self.bleed_right_mm = self._safe_non_negative_number(
            bleed.get(
                "droite",
                0.0,
            ),
            default=0.0,
        )
        self.bleed_bottom_mm = self._safe_non_negative_number(
            bleed.get(
                "bas",
                0.0,
            ),
            default=0.0,
        )
        self.bleed_left_mm = self._safe_non_negative_number(
            bleed.get(
                "gauche",
                0.0,
            ),
            default=0.0,
        )

        loaded_background = layout.get(
            "fond",
            {},
        )

        self.background = self._normalize_background(
            loaded_background
        )

    # ==========================================================
    # Sécurité
    # ==========================================================

    def _ensure_editable(self) -> None:
        if self.locked:
            raise RuntimeError(
                "Cette page est verrouillée et ne peut pas être modifiée."
            )

    def _require_root(self) -> Path:
        if self.root is None:
            raise RuntimeError(
                "La page n'a pas encore de dossier."
            )

        return self.root

    # ==========================================================
    # Fond
    # ==========================================================

    def _default_background(self) -> dict[str, Any]:
        return {
            "nature": "aucun",
            "active": False,
            "ressource": "",
            "portee": "page",
            "mode": "remplir",
            "conserver_proportions": True,
            "opacite": 1.0,
            "cadre_automatique": True,
            "x_mm": 0.0,
            "y_mm": 0.0,
            "largeur_mm": self.width_mm,
            "hauteur_mm": self.height_mm,
            "rotation": 0.0,
        }

    def _normalize_background(
        self,
        background: dict,
    ) -> dict[str, Any]:
        if not isinstance(background, dict):
            return self._default_background()

        scope = self._normalize_background_scope(
            background.get(
                "portee",
                "page",
            )
        )

        fit_mode = self._normalize_background_fit_mode(
            background.get(
                "mode",
                "remplir",
            )
        )

        target = self._background_target_box(scope)

        raw_nature = str(
            background.get(
                "nature",
                "fixe" if background.get("active") else "aucun",
            )
        ).strip().lower()
        nature = (
            raw_nature
            if raw_nature in {"aucun", "fixe", "variable"}
            else "aucun"
        )
        active = bool(
            background.get(
                "active",
                False,
            )
        )
        if nature != "fixe":
            active = False

        return {
            "nature": nature,
            "active": active,
            "ressource": str(
                background.get(
                    "ressource",
                    "",
                )
            ),
            "portee": scope,
            "mode": fit_mode,
            "conserver_proportions": bool(
                background.get(
                    "conserver_proportions",
                    True,
                )
            ),
            "opacite": self._safe_opacity(
                background.get(
                    "opacite",
                    1.0,
                )
            ),
            "cadre_automatique": bool(
                background.get(
                    "cadre_automatique",
                    fit_mode != "manuel",
                )
            ),
            "x_mm": self._safe_number(
                background.get(
                    "x_mm",
                    target["x"],
                ),
                default=target["x"],
            ),
            "y_mm": self._safe_number(
                background.get(
                    "y_mm",
                    target["y"],
                ),
                default=target["y"],
            ),
            "largeur_mm": self._safe_positive_number(
                background.get(
                    "largeur_mm",
                    target["largeur"],
                ),
                default=target["largeur"],
            ),
            "hauteur_mm": self._safe_positive_number(
                background.get(
                    "hauteur_mm",
                    target["hauteur"],
                ),
                default=target["hauteur"],
            ),
            "rotation": self._normalize_rotation(
                background.get(
                    "rotation",
                    0.0,
                )
            ),
        }

    def _background_target_box(
        self,
        scope: str,
    ) -> dict[str, float]:
        if scope == "surface_composition":
            return self.composition_box_mm()

        if scope == "fonds_perdus":
            return {
                "x": -self.bleed_left_mm,
                "y": -self.bleed_top_mm,
                "largeur": self.width_mm + self.bleed_left_mm + self.bleed_right_mm,
                "hauteur": self.height_mm + self.bleed_top_mm + self.bleed_bottom_mm,
            }

        return {
            "x": 0.0,
            "y": 0.0,
            "largeur": self.width_mm,
            "hauteur": self.height_mm,
        }

    def _reset_background_frame_if_automatic(self) -> None:
        if (
            not self.background.get("active")
            and self.background.get("nature", "aucun") != "variable"
        ):
            return

        if not self.background.get("cadre_automatique", True):
            return

        scope = self._normalize_background_scope(
            self.background.get(
                "portee",
                "page",
            )
        )

        target = self._background_target_box(scope)

        self.background.update(
            {
                "x_mm": target["x"],
                "y_mm": target["y"],
                "largeur_mm": target["largeur"],
                "hauteur_mm": target["hauteur"],
            }
        )

    # ==========================================================
    # Normalisation
    # ==========================================================

    @classmethod
    def _normalize_page_kind(
        cls,
        page_kind: str,
    ) -> str:
        normalized = str(page_kind).strip().lower()

        if normalized not in cls.PAGE_KINDS:
            return cls.DEFAULT_KIND

        return normalized

    @classmethod
    def _normalize_workspace(
        cls,
        workspace: str,
        *,
        allow_empty: bool = False,
    ) -> str:
        normalized = str(workspace).strip().lower()

        if allow_empty and not normalized:
            return ""

        if normalized not in cls.WORKSPACES:
            raise ValueError(
                f"Espace de travail inconnu : {workspace}"
            )

        return normalized

    @classmethod
    def _default_workspaces_for_kind(
        cls,
        page_kind: str,
    ) -> tuple[str, str]:
        if page_kind == "page_produite":
            return (
                "",
                "production",
            )

        if page_kind == "page_textuelle":
            return (
                "",
                "composition",
            )

        return (
            "atelier",
            "atelier",
        )

    @classmethod
    def _normalize_orientation(
        cls,
        orientation: str,
    ) -> str:
        normalized = str(orientation).strip().capitalize()

        if normalized not in cls.ORIENTATIONS:
            return cls.DEFAULT_ORIENTATION

        return normalized

    @classmethod
    def _normalize_background_scope(
        cls,
        scope: str,
    ) -> str:
        normalized = str(scope).strip().lower()

        if normalized not in cls.BACKGROUND_SCOPES:
            raise ValueError(
                f"Portée de fond inconnue : {scope}"
            )

        return normalized

    @classmethod
    def _normalize_background_fit_mode(
        cls,
        fit_mode: str,
    ) -> str:
        normalized = str(fit_mode).strip().lower()

        # Compatibilité avec les premières versions : l'ancien mode
        # « étirer » devient un cadre manuel couvrant la surface choisie.
        if normalized == "etirer":
            return "manuel"

        if normalized not in cls.BACKGROUND_FIT_MODES:
            raise ValueError(
                f"Mode de fond inconnu : {fit_mode}"
            )

        return normalized

    @staticmethod
    def _oriented_size(
        width: float,
        height: float,
        orientation: str,
    ) -> tuple[float, float]:
        if orientation == "Paysage" and height > width:
            return (
                height,
                width,
            )

        if orientation == "Portrait" and width > height:
            return (
                height,
                width,
            )

        return (
            width,
            height,
        )

    # ==========================================================
    # Valeurs numériques
    # ==========================================================

    @staticmethod
    def _validate_number(
        value: float,
        label: str,
    ) -> float:
        if isinstance(value, bool):
            raise TypeError(
                f"{label.capitalize()} doit être un nombre."
            )

        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise TypeError(
                f"{label.capitalize()} doit être un nombre."
            ) from error

        if number != number or number in {float("inf"), float("-inf")}:
            raise ValueError(
                f"{label.capitalize()} doit être une valeur finie."
            )

        return number

    @classmethod
    def _validate_positive_number(
        cls,
        value: float,
        label: str,
    ) -> float:
        number = cls._validate_number(
            value,
            label,
        )

        if number <= 0:
            raise ValueError(
                f"{label.capitalize()} doit être supérieur à zéro."
            )

        return number

    @classmethod
    def _validate_non_negative_number(
        cls,
        value: float,
        label: str,
    ) -> float:
        number = cls._validate_number(
            value,
            label,
        )

        if number < 0:
            raise ValueError(
                f"{label.capitalize()} ne peut pas être négatif."
            )

        return number

    @classmethod
    def _validate_opacity(
        cls,
        value: float,
    ) -> float:
        opacity = cls._validate_number(
            value,
            "opacité",
        )

        if not 0.0 <= opacity <= 1.0:
            raise ValueError(
                "L'opacité doit être comprise entre 0 et 1."
            )

        return opacity

    @staticmethod
    def _normalize_rotation(
        value: float,
    ) -> float:
        return Page._validate_number(
            value,
            "rotation",
        ) % 360.0

    @classmethod
    def _safe_number(
        cls,
        value: Any,
        *,
        default: float,
    ) -> float:
        try:
            return cls._validate_number(
                value,
                "valeur",
            )
        except (TypeError, ValueError):
            return float(default)

    @classmethod
    def _safe_positive_number(
        cls,
        value: Any,
        *,
        default: float,
    ) -> float:
        try:
            return cls._validate_positive_number(
                value,
                "valeur",
            )
        except (TypeError, ValueError):
            return float(default)

    @classmethod
    def _safe_non_negative_number(
        cls,
        value: Any,
        *,
        default: float,
    ) -> float:
        try:
            return cls._validate_non_negative_number(
                value,
                "valeur",
            )
        except (TypeError, ValueError):
            return float(default)

    @classmethod
    def _safe_opacity(
        cls,
        value: Any,
    ) -> float:
        try:
            return cls._validate_opacity(
                value
            )
        except (TypeError, ValueError):
            return 1.0

    @staticmethod
    def _safe_int(
        value: Any,
        *,
        default: int,
    ) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"identifier={self.identifier!r}, "
            f"number={self.number}, "
            f"title={self.display_title!r}, "
            f"type={self.page_type!r}, "
            f"kind={self.page_kind!r}, "
            f"state={self.state!r}, "
            f"zones={self.zone_count}, "
            f"locked={self.locked})"
        )