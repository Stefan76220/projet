from __future__ import annotations

from src.core.project import Project


class ProjectManager:
    """
    Gestionnaire du projet courant.
    """

    def __init__(self) -> None:

        self.current_project: Project | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def has_project(self) -> bool:

        return self.current_project is not None

    @property
    def project(self) -> Project:

        return self.require_project()

    # ==========================================================
    # Gestion des projets
    # ==========================================================

    def new_project(
        self,
        folder: str,
        name: str,
    ) -> Project:

        project = Project()

        project.create(
            folder,
            name,
        )

        self.current_project = project

        return project

    def open_project(
        self,
        folder: str,
    ) -> Project:

        project = Project()

        project.load(
            folder,
        )

        self.current_project = project

        return project

    def close_project(self) -> None:

        self.current_project = None

    # ==========================================================
    # Accès
    # ==========================================================

    def get_project(self) -> Project | None:

        return self.current_project

    def get_project_name(self) -> str:

        if not self.has_project:
            return ""

        return self.current_project.name

    # ==========================================================
    # Vérifications
    # ==========================================================

    def require_project(self) -> Project:

        if self.current_project is None:
            raise RuntimeError(
                "Aucun projet ouvert."
            )

        return self.current_project

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"project={self.current_project!r})"
        )