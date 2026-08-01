from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from math import isfinite
from typing import Any
from uuid import uuid4


class Zone:
    """
    Zone polyvalente utilisée par les pages de PageMaître.

    Une zone définit une forme, une géométrie et un comportement.
    Elle ne possède aucune spécialité imposée : son contenu peut être
    remplacé par du texte, une image, un tableau, une donnée ou tout
    autre composant pris en charge par l'application.
    """

    VERSION = "1.0"
    ELEMENT_TYPE = "zone"

    DEFAULT_SHAPE = "rectangle"
    DEFAULT_ROLE = "libre"
    DEFAULT_ANCHOR = "page"
    DEFAULT_TEXT_WRAP = "aucun"

    SHAPES = {
        "rectangle",
        "ellipse",
        "cercle",
        "forme_libre",
    }

    ROLES = {
        "libre",
        "fixe",
        "remplissable",
    }

    ANCHORS = {
        "page",
        "surface_composition",
        "paragraphe",
        "caractere",
    }

    TEXT_WRAPS = {
        "aucun",
        "parallele",
        "optimal",
        "avant",
        "apres",
        "continu",
        "arriere_plan",
        "contour",
    }

    CONTENT_SOURCES = {
        "manuel",
        "bibliotheque",
        "import",
        "ia",
    }

    CROP_MODES = {
        "remplir",
        "ajuster",
        "etirer",
        "original",
    }

    HORIZONTAL_ALIGNMENTS = {
        "gauche",
        "centre",
        "droite",
    }

    VERTICAL_ALIGNMENTS = {
        "haut",
        "centre",
        "bas",
    }

    TEXT_OVERFLOW_MODES = {
        "masquer",
        "adapter",
        "continuer",
    }

    def __init__(
        self,
        *,
        name: str = "",
        shape: str = DEFAULT_SHAPE,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 100.0,
        height: float = 100.0,
    ) -> None:
        now = datetime.now().isoformat()

        # Identité
        self.identifier = str(uuid4())
        self.name = name.strip()

        # Géométrie
        self.shape = self._normalize_choice(
            shape,
            self.SHAPES,
            self.DEFAULT_SHAPE,
            "forme",
        )
        self.x = self._validate_number(x, "x")
        self.y = self._validate_number(y, "y")
        self.width = self._validate_size(width, "largeur")
        self.height = self._validate_size(height, "hauteur")
        self.rotation = 0.0
        self.z_index = 0

        # Apparence
        self.fill = "#FFFFFF00"
        self.stroke = "#000000"
        self.stroke_width = 1.0
        self.opacity = 1.0
        self.corner_radius = 0.0

        # Comportement général
        self.visible = True
        self.locked = False
        self.role = self.DEFAULT_ROLE

        # Champ de modèle
        self.field_id = ""
        self.field_label = ""
        self.required = False
        self.allowed_content_types: list[str] = []
        self.allowed_sources: list[str] = sorted(self.CONTENT_SOURCES)

        # Contenu interchangeable
        self.content_type = ""
        self.content_value: Any = None
        self.resource = ""
        self.content_metadata: dict[str, Any] = {}

        # Cadrage du contenu visuel
        self.crop_mode = "remplir"
        self.horizontal_alignment = "centre"
        self.vertical_alignment = "centre"
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.zoom = 1.0
        self.keep_aspect_ratio = True

        # Insertion dans la composition textuelle
        self.anchor = self.DEFAULT_ANCHOR
        self.text_wrap = self.DEFAULT_TEXT_WRAP
        self.wrap_margin_top = 0.0
        self.wrap_margin_right = 0.0
        self.wrap_margin_bottom = 0.0
        self.wrap_margin_left = 0.0

        # Débordement et continuité du texte
        self.text_overflow = "masquer"
        self.next_zone_id = ""

        # Regroupement
        self.group_id = ""

        # Dates
        self.created = now
        self.modified = now

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def display_name(self) -> str:
        return self.name or f"Zone {self.identifier[:8]}"

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return (
            self.x,
            self.y,
            self.width,
            self.height,
        )

    @property
    def is_fillable(self) -> bool:
        return self.role == "remplissable"

    @property
    def is_fixed(self) -> bool:
        return self.role == "fixe"

    @property
    def has_content(self) -> bool:
        return bool(
            self.content_type
            or self.resource
            or self.content_value not in (None, "")
        )

    # ==========================================================
    # Géométrie
    # ==========================================================

    def set_geometry(
        self,
        *,
        x: float | None = None,
        y: float | None = None,
        width: float | None = None,
        height: float | None = None,
        rotation: float | None = None,
    ) -> None:
        self._ensure_editable()

        if x is not None:
            self.x = self._validate_number(x, "x")

        if y is not None:
            self.y = self._validate_number(y, "y")

        if width is not None:
            self.width = self._validate_size(width, "largeur")

        if height is not None:
            self.height = self._validate_size(height, "hauteur")

        if rotation is not None:
            self.rotation = self._normalize_rotation(rotation)

        self._touch()

    def move(
        self,
        delta_x: float,
        delta_y: float,
    ) -> None:
        self._ensure_editable()

        self.x += self._validate_number(delta_x, "déplacement horizontal")
        self.y += self._validate_number(delta_y, "déplacement vertical")

        self._touch()

    def resize(
        self,
        width: float,
        height: float,
        *,
        keep_ratio: bool = False,
    ) -> None:
        self._ensure_editable()

        new_width = self._validate_size(width, "largeur")
        new_height = self._validate_size(height, "hauteur")

        if keep_ratio and self.height > 0:
            ratio = self.width / self.height
            requested_ratio = new_width / new_height

            if requested_ratio > ratio:
                new_width = new_height * ratio
            else:
                new_height = new_width / ratio

        self.width = new_width
        self.height = new_height

        self._touch()

    def set_rotation(
        self,
        angle: float,
    ) -> None:
        self._ensure_editable()
        self.rotation = self._normalize_rotation(angle)
        self._touch()

    def set_z_index(
        self,
        z_index: int,
    ) -> None:
        self._ensure_editable()

        if isinstance(z_index, bool) or not isinstance(z_index, int):
            raise TypeError("L'ordre de superposition doit être un entier.")

        self.z_index = z_index
        self._touch()

    # ==========================================================
    # Apparence
    # ==========================================================

    def set_style(
        self,
        *,
        fill: str | None = None,
        stroke: str | None = None,
        stroke_width: float | None = None,
        opacity: float | None = None,
        corner_radius: float | None = None,
    ) -> None:
        self._ensure_editable()

        if fill is not None:
            self.fill = str(fill).strip()

        if stroke is not None:
            self.stroke = str(stroke).strip()

        if stroke_width is not None:
            self.stroke_width = self._validate_non_negative(
                stroke_width,
                "épaisseur du contour",
            )

        if opacity is not None:
            opacity_value = self._validate_number(opacity, "opacité")

            if not 0.0 <= opacity_value <= 1.0:
                raise ValueError("L'opacité doit être comprise entre 0 et 1.")

            self.opacity = opacity_value

        if corner_radius is not None:
            self.corner_radius = self._validate_non_negative(
                corner_radius,
                "rayon des angles",
            )

        self._touch()

    # ==========================================================
    # Rôle dans une page ou un modèle
    # ==========================================================

    def set_role(
        self,
        role: str,
    ) -> None:
        self._ensure_editable()
        self.role = self._normalize_choice(
            role,
            self.ROLES,
            self.DEFAULT_ROLE,
            "rôle",
        )
        self._touch()

    def configure_field(
        self,
        *,
        field_id: str,
        label: str = "",
        required: bool = False,
        allowed_content_types: list[str] | None = None,
        allowed_sources: list[str] | None = None,
    ) -> None:
        self._ensure_editable()

        normalized_field_id = field_id.strip()

        if self.role == "remplissable" and not normalized_field_id:
            raise ValueError(
                "Une zone remplissable doit posséder un identifiant de champ."
            )

        self.field_id = normalized_field_id
        self.field_label = label.strip()
        self.required = bool(required)

        if allowed_content_types is not None:
            self.allowed_content_types = self._normalize_string_list(
                allowed_content_types
            )

        if allowed_sources is not None:
            normalized_sources = self._normalize_string_list(allowed_sources)
            unknown_sources = set(normalized_sources) - self.CONTENT_SOURCES

            if unknown_sources:
                raise ValueError(
                    "Sources de contenu inconnues : "
                    + ", ".join(sorted(unknown_sources))
                )

            self.allowed_sources = normalized_sources

        self._touch()

    # ==========================================================
    # Contenu polyvalent
    # ==========================================================

    def set_content(
        self,
        *,
        content_type: str,
        value: Any = None,
        resource: str = "",
        source: str = "manuel",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        source = source.strip().lower()

        if source not in self.CONTENT_SOURCES:
            raise ValueError(f"Source de contenu inconnue : {source}")

        if self.allowed_sources and source not in self.allowed_sources:
            raise ValueError(
                f"La source « {source} » n'est pas autorisée pour cette zone."
            )

        normalized_content_type = content_type.strip().lower()

        if (
            self.allowed_content_types
            and normalized_content_type not in self.allowed_content_types
        ):
            raise ValueError(
                f"Le contenu « {normalized_content_type} » "
                "n'est pas autorisé pour cette zone."
            )

        self.content_type = normalized_content_type
        self.content_value = deepcopy(value)
        self.resource = resource.strip()
        self.content_metadata = deepcopy(metadata or {})
        self.content_metadata["source"] = source

        self._touch()

    def clear_content(self) -> None:
        self.content_type = ""
        self.content_value = None
        self.resource = ""
        self.content_metadata = {}
        self._touch()

    # ==========================================================
    # Cadrage du contenu visuel
    # ==========================================================

    def set_crop(
        self,
        *,
        mode: str | None = None,
        horizontal_alignment: str | None = None,
        vertical_alignment: str | None = None,
        offset_x: float | None = None,
        offset_y: float | None = None,
        zoom: float | None = None,
        keep_aspect_ratio: bool | None = None,
    ) -> None:
        if mode is not None:
            self.crop_mode = self._normalize_choice(
                mode,
                self.CROP_MODES,
                "remplir",
                "mode de cadrage",
            )

        if horizontal_alignment is not None:
            self.horizontal_alignment = self._normalize_choice(
                horizontal_alignment,
                self.HORIZONTAL_ALIGNMENTS,
                "centre",
                "alignement horizontal",
            )

        if vertical_alignment is not None:
            self.vertical_alignment = self._normalize_choice(
                vertical_alignment,
                self.VERTICAL_ALIGNMENTS,
                "centre",
                "alignement vertical",
            )

        if offset_x is not None:
            self.offset_x = self._validate_number(
                offset_x,
                "décalage horizontal",
            )

        if offset_y is not None:
            self.offset_y = self._validate_number(
                offset_y,
                "décalage vertical",
            )

        if zoom is not None:
            zoom_value = self._validate_number(zoom, "zoom")

            if zoom_value <= 0:
                raise ValueError("Le zoom doit être supérieur à zéro.")

            self.zoom = zoom_value

        if keep_aspect_ratio is not None:
            self.keep_aspect_ratio = bool(keep_aspect_ratio)

        self._touch()

    # ==========================================================
    # Composition textuelle
    # ==========================================================

    def set_text_layout(
        self,
        *,
        anchor: str | None = None,
        text_wrap: str | None = None,
        margin_top: float | None = None,
        margin_right: float | None = None,
        margin_bottom: float | None = None,
        margin_left: float | None = None,
        overflow: str | None = None,
        next_zone_id: str | None = None,
    ) -> None:
        if anchor is not None:
            self.anchor = self._normalize_choice(
                anchor,
                self.ANCHORS,
                self.DEFAULT_ANCHOR,
                "ancrage",
            )

        if text_wrap is not None:
            self.text_wrap = self._normalize_choice(
                text_wrap,
                self.TEXT_WRAPS,
                self.DEFAULT_TEXT_WRAP,
                "habillage",
            )

        if margin_top is not None:
            self.wrap_margin_top = self._validate_non_negative(
                margin_top,
                "marge haute d'habillage",
            )

        if margin_right is not None:
            self.wrap_margin_right = self._validate_non_negative(
                margin_right,
                "marge droite d'habillage",
            )

        if margin_bottom is not None:
            self.wrap_margin_bottom = self._validate_non_negative(
                margin_bottom,
                "marge basse d'habillage",
            )

        if margin_left is not None:
            self.wrap_margin_left = self._validate_non_negative(
                margin_left,
                "marge gauche d'habillage",
            )

        if overflow is not None:
            self.text_overflow = self._normalize_choice(
                overflow,
                self.TEXT_OVERFLOW_MODES,
                "masquer",
                "débordement du texte",
            )

        if next_zone_id is not None:
            self.next_zone_id = next_zone_id.strip()

        self._touch()

    # ==========================================================
    # Verrouillage
    # ==========================================================

    def set_locked(
        self,
        locked: bool,
    ) -> None:
        self.locked = bool(locked)
        self._touch()

    # ==========================================================
    # Duplication
    # ==========================================================

    def clone(
        self,
        *,
        keep_content: bool = True,
    ) -> Zone:
        clone = Zone.from_dict(self.to_dict())

        clone.identifier = str(uuid4())
        clone.name = self._copy_name(self.display_name)

        now = datetime.now().isoformat()
        clone.created = now
        clone.modified = now
        clone.locked = False

        if not keep_content:
            clone.clear_content()

        return clone

    # ==========================================================
    # Sérialisation
    # ==========================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.ELEMENT_TYPE,
            "version": self.VERSION,
            "identite": {
                "identifiant": self.identifier,
                "nom": self.name,
            },
            "geometrie": {
                "forme": self.shape,
                "x": self.x,
                "y": self.y,
                "largeur": self.width,
                "hauteur": self.height,
                "rotation": self.rotation,
                "ordre": self.z_index,
            },
            "apparence": {
                "fond": self.fill,
                "contour": self.stroke,
                "epaisseur_contour": self.stroke_width,
                "opacite": self.opacity,
                "rayon_angles": self.corner_radius,
            },
            "comportement": {
                "visible": self.visible,
                "verrouillee": self.locked,
                "role": self.role,
                "groupe": self.group_id,
            },
            "champ": {
                "identifiant": self.field_id,
                "libelle": self.field_label,
                "obligatoire": self.required,
                "types_contenu_autorises": list(self.allowed_content_types),
                "sources_autorisees": list(self.allowed_sources),
            },
            "contenu": {
                "type": self.content_type,
                "valeur": deepcopy(self.content_value),
                "ressource": self.resource,
                "metadonnees": deepcopy(self.content_metadata),
            },
            "cadrage": {
                "mode": self.crop_mode,
                "alignement_horizontal": self.horizontal_alignment,
                "alignement_vertical": self.vertical_alignment,
                "decalage_x": self.offset_x,
                "decalage_y": self.offset_y,
                "zoom": self.zoom,
                "conserver_proportions": self.keep_aspect_ratio,
            },
            "composition_textuelle": {
                "ancrage": self.anchor,
                "habillage": self.text_wrap,
                "marges_habillage": {
                    "haut": self.wrap_margin_top,
                    "droite": self.wrap_margin_right,
                    "bas": self.wrap_margin_bottom,
                    "gauche": self.wrap_margin_left,
                },
                "debordement": self.text_overflow,
                "zone_suivante": self.next_zone_id,
            },
            "dates": {
                "creation": self.created,
                "modification": self.modified,
            },
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Zone:
        identity = data.get("identite", {})
        geometry = data.get("geometrie", {})
        appearance = data.get("apparence", {})
        behavior = data.get("comportement", {})
        field = data.get("champ", {})
        content = data.get("contenu", {})
        crop = data.get("cadrage", {})
        text_layout = data.get("composition_textuelle", {})
        wrap_margins = text_layout.get("marges_habillage", {})
        dates = data.get("dates", {})

        zone = cls(
            name=str(identity.get("nom", "")),
            shape=str(
                geometry.get(
                    "forme",
                    cls.DEFAULT_SHAPE,
                )
            ),
            x=geometry.get("x", 0.0),
            y=geometry.get("y", 0.0),
            width=geometry.get("largeur", 100.0),
            height=geometry.get("hauteur", 100.0),
        )

        zone.identifier = str(
            identity.get(
                "identifiant",
                str(uuid4()),
            )
        )

        zone.rotation = zone._normalize_rotation(
            geometry.get("rotation", 0.0)
        )

        z_index = geometry.get("ordre", 0)

        if isinstance(z_index, bool) or not isinstance(z_index, int):
            z_index = int(z_index)

        zone.z_index = z_index

        zone.fill = str(appearance.get("fond", "#FFFFFF00"))
        zone.stroke = str(appearance.get("contour", "#000000"))
        zone.stroke_width = zone._validate_non_negative(
            appearance.get("epaisseur_contour", 1.0),
            "épaisseur du contour",
        )

        opacity = zone._validate_number(
            appearance.get("opacite", 1.0),
            "opacité",
        )
        zone.opacity = min(1.0, max(0.0, opacity))

        zone.corner_radius = zone._validate_non_negative(
            appearance.get("rayon_angles", 0.0),
            "rayon des angles",
        )

        zone.visible = bool(behavior.get("visible", True))
        zone.locked = bool(behavior.get("verrouillee", False))
        zone.role = zone._normalize_choice(
            str(behavior.get("role", cls.DEFAULT_ROLE)),
            cls.ROLES,
            cls.DEFAULT_ROLE,
            "rôle",
        )
        zone.group_id = str(behavior.get("groupe", ""))

        zone.field_id = str(field.get("identifiant", ""))
        zone.field_label = str(field.get("libelle", ""))
        zone.required = bool(field.get("obligatoire", False))
        zone.allowed_content_types = zone._normalize_string_list(
            field.get("types_contenu_autorises", [])
        )

        loaded_sources = zone._normalize_string_list(
            field.get(
                "sources_autorisees",
                sorted(cls.CONTENT_SOURCES),
            )
        )
        zone.allowed_sources = [
            source
            for source in loaded_sources
            if source in cls.CONTENT_SOURCES
        ]

        zone.content_type = str(content.get("type", "")).strip().lower()
        zone.content_value = deepcopy(content.get("valeur"))
        zone.resource = str(content.get("ressource", ""))
        zone.content_metadata = deepcopy(
            content.get("metadonnees", {})
        )

        zone.crop_mode = zone._normalize_choice(
            str(crop.get("mode", "remplir")),
            cls.CROP_MODES,
            "remplir",
            "mode de cadrage",
        )
        zone.horizontal_alignment = zone._normalize_choice(
            str(crop.get("alignement_horizontal", "centre")),
            cls.HORIZONTAL_ALIGNMENTS,
            "centre",
            "alignement horizontal",
        )
        zone.vertical_alignment = zone._normalize_choice(
            str(crop.get("alignement_vertical", "centre")),
            cls.VERTICAL_ALIGNMENTS,
            "centre",
            "alignement vertical",
        )
        zone.offset_x = zone._validate_number(
            crop.get("decalage_x", 0.0),
            "décalage horizontal",
        )
        zone.offset_y = zone._validate_number(
            crop.get("decalage_y", 0.0),
            "décalage vertical",
        )

        zoom = zone._validate_number(
            crop.get("zoom", 1.0),
            "zoom",
        )
        zone.zoom = zoom if zoom > 0 else 1.0
        zone.keep_aspect_ratio = bool(
            crop.get("conserver_proportions", True)
        )

        zone.anchor = zone._normalize_choice(
            str(text_layout.get("ancrage", cls.DEFAULT_ANCHOR)),
            cls.ANCHORS,
            cls.DEFAULT_ANCHOR,
            "ancrage",
        )
        zone.text_wrap = zone._normalize_choice(
            str(text_layout.get("habillage", cls.DEFAULT_TEXT_WRAP)),
            cls.TEXT_WRAPS,
            cls.DEFAULT_TEXT_WRAP,
            "habillage",
        )
        zone.wrap_margin_top = zone._validate_non_negative(
            wrap_margins.get("haut", 0.0),
            "marge haute d'habillage",
        )
        zone.wrap_margin_right = zone._validate_non_negative(
            wrap_margins.get("droite", 0.0),
            "marge droite d'habillage",
        )
        zone.wrap_margin_bottom = zone._validate_non_negative(
            wrap_margins.get("bas", 0.0),
            "marge basse d'habillage",
        )
        zone.wrap_margin_left = zone._validate_non_negative(
            wrap_margins.get("gauche", 0.0),
            "marge gauche d'habillage",
        )
        zone.text_overflow = zone._normalize_choice(
            str(text_layout.get("debordement", "masquer")),
            cls.TEXT_OVERFLOW_MODES,
            "masquer",
            "débordement du texte",
        )
        zone.next_zone_id = str(
            text_layout.get("zone_suivante", "")
        )

        zone.created = str(
            dates.get(
                "creation",
                zone.created,
            )
        )
        zone.modified = str(
            dates.get(
                "modification",
                zone.modified,
            )
        )

        return zone

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self) -> list[str]:
        errors: list[str] = []

        if self.width <= 0:
            errors.append("La largeur doit être supérieure à zéro.")

        if self.height <= 0:
            errors.append("La hauteur doit être supérieure à zéro.")

        if self.role == "remplissable" and not self.field_id:
            errors.append(
                "Une zone remplissable doit posséder un identifiant de champ."
            )

        if self.required and self.role != "remplissable":
            errors.append(
                "Seule une zone remplissable peut être obligatoire."
            )

        if self.required and not self.has_content:
            errors.append(
                f"La zone obligatoire « {self.display_name} » est vide."
            )

        if (
            self.allowed_content_types
            and self.content_type
            and self.content_type not in self.allowed_content_types
        ):
            errors.append(
                f"Le type de contenu « {self.content_type} » "
                "n'est pas autorisé."
            )

        if self.text_overflow == "continuer" and not self.next_zone_id:
            errors.append(
                "Une zone dont le texte continue doit désigner "
                "la zone suivante."
            )

        return errors

    # ==========================================================
    # Utilitaires privés
    # ==========================================================

    def _ensure_editable(self) -> None:
        if self.locked:
            raise RuntimeError(
                "Cette zone est verrouillée et ne peut pas être modifiée."
            )

    def _touch(self) -> None:
        self.modified = datetime.now().isoformat()

    @staticmethod
    def _validate_number(
        value: float,
        label: str,
    ) -> float:
        if isinstance(value, bool):
            raise TypeError(f"{label.capitalize()} doit être un nombre.")

        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise TypeError(
                f"{label.capitalize()} doit être un nombre."
            ) from error

        if not isfinite(number):
            raise ValueError(
                f"{label.capitalize()} doit être une valeur finie."
            )

        return number

    @classmethod
    def _validate_size(
        cls,
        value: float,
        label: str,
    ) -> float:
        number = cls._validate_number(value, label)

        if number <= 0:
            raise ValueError(
                f"{label.capitalize()} doit être supérieur à zéro."
            )

        return number

    @classmethod
    def _validate_non_negative(
        cls,
        value: float,
        label: str,
    ) -> float:
        number = cls._validate_number(value, label)

        if number < 0:
            raise ValueError(
                f"{label.capitalize()} ne peut pas être négatif."
            )

        return number

    @staticmethod
    def _normalize_choice(
        value: str,
        allowed_values: set[str],
        default: str,
        label: str,
    ) -> str:
        normalized = str(value).strip().lower()

        if not normalized:
            return default

        if normalized not in allowed_values:
            raise ValueError(
                f"{label.capitalize()} inconnu : {normalized}"
            )

        return normalized

    @staticmethod
    def _normalize_rotation(
        angle: float,
    ) -> float:
        number = Zone._validate_number(angle, "rotation")
        return number % 360.0

    @staticmethod
    def _normalize_string_list(
        values: list[str] | tuple[str, ...] | set[str],
    ) -> list[str]:
        normalized: list[str] = []

        for value in values:
            item = str(value).strip().lower()

            if item and item not in normalized:
                normalized.append(item)

        return normalized

    @staticmethod
    def _copy_name(
        name: str,
    ) -> str:
        clean_name = name.strip() or "Zone"

        if clean_name.endswith(" (copie)"):
            return clean_name

        return f"{clean_name} (copie)"

    # ==========================================================
    # Représentation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"identifier={self.identifier!r}, "
            f"name={self.display_name!r}, "
            f"shape={self.shape!r}, "
            f"role={self.role!r}, "
            f"bounds={self.bounds!r})"
        )