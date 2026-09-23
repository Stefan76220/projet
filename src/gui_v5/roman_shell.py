from __future__ import annotations

"""Coque GUI V5 Roman.

La V5 ne recopie pas l'interface stable. Elle herite de la coque V4 figee et
intercepte uniquement la porte de navigation commune ``_activate_page``.

Ainsi Structure, Aller, Precedente, Suivante et le Survol V4 transitoire
continuent d'utiliser le rendu valide, mais chaque activation de page est
d'abord enregistree dans l'unique ``NavigationState`` de ``RomanSession``.

Le remplacement du panneau Survol d'observation par le parcours decisionnel
V5 est volontairement un jalon suivant : ce fichier ne melange pas rendu et
moteur de revue.
"""

from typing import Any

from src.gui_v4.settings_shell import TomeLineaV4SettingsStage

from tomelinea.project_types.roman import RomanSession


class TomeLineaV5RomanStage(
    TomeLineaV4SettingsStage
):
    """Hote graphique V5 du Roman, construit sur la coque V4 validee."""

    def __init__(
        self,
        *,
        defer_show: bool = False,
    ) -> None:
        self._v5_roman_session: RomanSession | None = None
        self._v5_roman_project: Any = None
        self._v5_roman_book: Any = None

        super().__init__(
            defer_show=defer_show
        )

        try:
            self.title(
                "TomeLinea V5"
            )
        except Exception:
            pass

    @property
    def v5_roman_session(
        self,
    ) -> RomanSession | None:
        return self._v5_roman_session

    def _v5_current_project(
        self,
    ) -> Any:
        workspace = getattr(
            self,
            "session",
            None,
        )

        if workspace is None:
            return None

        return getattr(
            workspace,
            "project",
            None,
        )

    def _v5_ensure_roman_session(
        self,
    ) -> RomanSession | None:
        project = self._v5_current_project()

        if project is None:
            self._v5_roman_session = None
            self._v5_roman_project = None
            self._v5_roman_book = None
            return None

        book = getattr(
            project,
            "book",
            None,
        )

        if book is None:
            self._v5_roman_session = None
            self._v5_roman_project = project
            self._v5_roman_book = None
            return None

        current = self._v5_roman_session

        if (
            current is not None
            and self._v5_roman_project is project
            and self._v5_roman_book is book
            and current.project is project
            and current.book is book
        ):
            return current

        current = RomanSession(
            project
        )

        self._v5_roman_session = current
        self._v5_roman_project = project
        self._v5_roman_book = book

        return current

    def _v5_apply_navigation_target(
        self,
        page_id: str,
        *,
        preserve_page_selection: bool = False,
    ) -> None:
        """Rend une cible deja demandee sans creer une seconde demande V5."""

        super()._activate_page(
            str(
                page_id
            ),
            preserve_page_selection=preserve_page_selection,
        )

    def _activate_page(
        self,
        page_id: str,
        *,
        preserve_page_selection: bool = False,
    ) -> None:
        """Porte unique V5 : Navigation commune d'abord, rendu V4 ensuite."""

        page_id = str(
            page_id
        )

        roman = self._v5_ensure_roman_session()

        if roman is not None:
            target = roman.navigation.request_page(
                roman.book,
                page_id,
            )

            if target.page_id != page_id:
                raise RuntimeError(
                    "La Navigation V5 n'a pas conserve la page demandee."
                )

        self._v5_apply_navigation_target(
            page_id,
            preserve_page_selection=preserve_page_selection,
        )


__all__ = [
    "TomeLineaV5RomanStage",
]