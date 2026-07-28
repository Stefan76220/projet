from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4


class Page:
    """
    Représentation complète d'une page éditoriale.
    """

    VERSION = "2.0"

    DEFAULT_TYPE = "Page vide"
    DEFAULT_STATE = "Brouillon"
    DEFAULT_COLOR = "#D9D4C7"
    DEFAULT_ICON = "📄"

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

        # Informations
        self.author = ""
        self.description = ""
        self.tags: list[str] = []

        # Mise en page
        self.format = "A5"
        self.orientation = "Portrait"

        # Contenu
        self.content: dict = {}
        self.elements: list[dict] = []

        # Historique
        self.history: list[dict] = []

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

        self.number = identity.get(
            "numero",
            1,
        )

        self.title = identity.get(
            "nom",
            "",
        )

        self.page_type = identity.get(
            "type",
            self.DEFAULT_TYPE,
        )

        # Compatibilité avec les anciennes pages
        self.state = editorial.get(
            "etat",
            identity.get(
                "etat",
                self.DEFAULT_STATE,
            ),
        )

        self.color = editorial.get(
            "couleur",
            self.DEFAULT_COLOR,
        )

        self.icon = editorial.get(
            "icone",
            self.DEFAULT_ICON,
        )

        self.locked = bool(
            editorial.get(
                "verrouillee",
                False,
            )
        )

        # Métadonnées
        self.author = metadata.get(
            "auteur",
            "",
        )

        self.created = metadata.get(
            "creation",
            "",
        )

        self.modified = metadata.get(
            "modification",
            "",
        )

        self.description = metadata.get(
            "description",
            "",
        )

        self.tags = list(
            metadata.get(
                "mots_cles",
                [],
            )
        )

        # Mise en page
        self.format = layout.get(
            "format",
            "A5",
        )

        self.orientation = layout.get(
            "orientation",
            "Portrait",
        )

        # Contenu
        self.content = dict(
            data.get(
                "contenu",
                {},
            )
        )

        self.elements = list(
            data.get(
                "elements",
                [],
            )
        )

        self.history = list(
            data.get(
                "historique",
                [],
            )
        )

        return self

    # ==========================================================
    # Modification
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

    def get_elements_by_type(
        self,
        element_type: str,
    ) -> list[dict]:
        """Retourne une copie des éléments correspondant au type demandé."""

        return [
            dict(element)
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

        Cette méthode centralise la persistance des objets éditoriaux
        dans le modèle Page plutôt que dans l'interface graphique.
        """

        self._ensure_editable()

        preserved_elements = [
            element
            for element in self.elements
            if element.get("type") != element_type
        ]

        normalized_elements = []

        for element in elements:
            normalized_element = dict(element)
            normalized_element["type"] = element_type
            normalized_elements.append(normalized_element)

        self.elements = preserved_elements + normalized_elements

        if save:
            self.save(update_history=False)

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
            "etat": self.state,
            "couleur": self.color,
            "icone": self.icon,
            "verrouillee": self.locked,
            "dossier": self.folder_name,
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
            "metadonnees": {
                "auteur": self.author,
                "creation": self.created,
                "modification": self.modified,
                "description": self.description,
                "mots_cles": self.tags,
            },
            "mise_en_page": {
                "format": self.format,
                "orientation": self.orientation,
            },
            "contenu": self.content,
            "elements": self.elements,
            "historique": self.history,
        }

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
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"identifier={self.identifier!r}, "
            f"number={self.number}, "
            f"title={self.display_title!r}, "
            f"type={self.page_type!r}, "
            f"state={self.state!r}, "
            f"locked={self.locked})"
        )