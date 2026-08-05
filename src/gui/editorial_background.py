from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
from PIL import Image


class EditorialBackground:
    """Fond éditorial réutilisable de PageMaître.

    Deux variantes sont disponibles :
    - ``accueil`` : décor plus visible pour la page d'accueil ;
    - ``soft`` : décor plus léger pour les espaces de travail.

    Le composant conserve les anciens paramètres de construction afin que les
    vues déjà créées continuent de fonctionner sans modification immédiate.
    """

    VARIANTS = {
        "accueil": "editorial_bg_accueil.png",
        "soft": "editorial_bg_soft.png",
    }

    def __init__(
        self,
        parent,
        *,
        variant: str = "accueil",
        left: bool = True,
        right: bool = True,
        size: tuple[int, int] | None = None,
        vertical_position: float = 0.5,
    ) -> None:
        self.parent = parent
        self.variant = variant if variant in self.VARIANTS else "soft"

        # Paramètres conservés pour compatibilité avec les vues existantes.
        self.left = left
        self.right = right
        self.size = size
        self.vertical_position = vertical_position

        self._source: Image.Image | None = None
        self._image: ctk.CTkImage | None = None
        self._label: ctk.CTkLabel | None = None
        self._configure_binding: str | None = None
        self._last_size = (0, 0)

    def place(self) -> None:
        """Place le fond sur toute la surface du conteneur parent."""

        path = self._find_asset_path(
            self.VARIANTS[self.variant]
        )
        if path is None:
            return

        try:
            self._source = Image.open(path).convert("RGB")
        except Exception:
            return

        width = max(self.parent.winfo_width(), 2)
        height = max(self.parent.winfo_height(), 2)

        self._image = ctk.CTkImage(
            light_image=self._source,
            dark_image=self._source,
            size=(width, height),
        )

        self._label = ctk.CTkLabel(
            self.parent,
            text="",
            image=self._image,
            fg_color="transparent",
            corner_radius=0,
        )
        self._label.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1,
        )
        # Le décor est créé avant les widgets de contenu : ils seront donc
        # naturellement affichés au-dessus. Ne pas utiliser ``lower()`` ici,
        # car CustomTkinter possède un canevas interne qui masquerait alors
        # complètement l'image derrière le fond du CTkFrame.

        self._configure_binding = self.parent.bind(
            "<Configure>",
            self._on_parent_resize,
            add="+",
        )

        self.parent.after_idle(self._fit_to_parent)

    def _on_parent_resize(self, _event=None) -> None:
        self._fit_to_parent()

    def _fit_to_parent(self) -> None:
        if self._image is None or self._label is None:
            return

        width = max(self.parent.winfo_width(), 2)
        height = max(self.parent.winfo_height(), 2)

        if (width, height) == self._last_size:
            return

        self._last_size = (width, height)
        self._image.configure(size=(width, height))
        self._label.configure(image=self._image)

    def set_variant(self, variant: str) -> None:
        """Change de variante sans recréer la vue qui utilise le décor."""

        if variant not in self.VARIANTS:
            raise ValueError(
                "La variante doit être 'accueil' ou 'soft'."
            )

        if variant == self.variant:
            return

        path = self._find_asset_path(
            self.VARIANTS[variant]
        )
        if path is None:
            return

        try:
            source = Image.open(path).convert("RGB")
        except Exception:
            return

        self.variant = variant
        self._source = source

        width = max(self.parent.winfo_width(), 2)
        height = max(self.parent.winfo_height(), 2)

        self._image = ctk.CTkImage(
            light_image=source,
            dark_image=source,
            size=(width, height),
        )

        if self._label is not None:
            self._label.configure(image=self._image)

        self._last_size = (width, height)

    def destroy(self) -> None:
        """Supprime proprement le décor et sa surveillance de taille."""

        if self._configure_binding is not None:
            try:
                self.parent.unbind(
                    "<Configure>",
                    self._configure_binding,
                )
            except Exception:
                pass
            self._configure_binding = None

        if self._label is not None:
            try:
                self._label.destroy()
            except Exception:
                pass
            self._label = None

        self._image = None
        self._source = None

    @staticmethod
    def _find_asset_path(filename: str) -> Path | None:
        project_root = Path(__file__).resolve().parents[2]
        candidates = (
            project_root
            / "assets"
            / "interface"
            / "backgrounds"
            / filename,
            Path.cwd()
            / "assets"
            / "interface"
            / "backgrounds"
            / filename,
        )

        for path in candidates:
            if path.is_file():
                return path

        return None