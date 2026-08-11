from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import customtkinter as ctk

from src.gui.views.dashboard_view import DashboardView
from src.gui.views.document_editor_view import DocumentEditorView
from src.gui.views.document_view import DocumentView
from src.gui.views.project_cleanup_dialog import ProjectCleanupDialog
from src.theme.colors import Colors


class Workspace:
    """Zone de travail principale de l'application."""

    RECENT_PROJECTS_LIMIT = 8
    BUREAU_LABELS = {
        "centre": "Centre du projet",
        "maquettage": "Maquettage",
        "atelier": "Atelier",
        "conception": "Conception",
        "assemblage": "Assemblage",
        "verification": "Vérification",
        "finalisation": "Finalisation",
    }
    DOCUMENT_VIEW_METHODS = {
        "maquettage": "_open_mockup",
        "atelier": "_open_model_workshop",
        "conception": "_open_atelier",
    }

    def __init__(
        self,
        parent,
        application,
    ) -> None:
        self.application = application
        self.current_project = None
        self._documents_transitioning = False
        self._cleanup_transitioning = False
        self._cleanup_view = None
        self._document_view = None

        self.frame = ctk.CTkFrame(
            parent,
            fg_color=Colors.WINDOW,
            corner_radius=0,
        )
        self.frame.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.show_dashboard()

    # ==========================================================
    # Gestion des vues
    # ==========================================================

    def clear(self) -> None:
        for widget in self.frame.winfo_children():
            widget.destroy()

        self._cleanup_view = None
        self._document_view = None

    def show_dashboard(self) -> None:
        self._destroy_cleanup_view()
        self._set_navigation_visible(False)
        self.clear()

        recent_projects = self._load_recent_projects()
        active_project = recent_projects[0] if recent_projects else None

        DashboardView(
            self.frame,
            recent_projects=recent_projects,
            active_project=active_project,
            on_open_recent=self._open_recent_project,
            on_open_workspace=self._open_recent_workspace,
            on_new_project=self._dashboard_new_project,
            on_open_project=self._dashboard_open_project,
        ).show()

    def show_documents(
        self,
        project,
        target_workspace: str | None = None,
    ) -> None:
        if self._documents_transitioning:
            return

        self._documents_transitioning = True
        self.current_project = project
        self._destroy_cleanup_view()
        self._record_project_activity(project)
        self._set_window_project_title(project)

        self.frame.grid_remove()

        try:
            self._set_navigation_visible(True)
            self.clear()

            content = ctk.CTkFrame(
                self.frame,
                fg_color=Colors.WINDOW,
                corner_radius=0,
            )
            content.pack(fill="both", expand=True)

            view = DocumentView(
                content,
                project,
                self.application,
                on_open_document=self.show_document,
                on_refresh=self.back_to_documents,
                on_cleanup=self.show_project_cleanup,
            )
            self._wrap_document_view_navigation(view, project)
            self._document_view = view
            view.show()

            self.frame.update_idletasks()

        finally:
            self.frame.grid(
                row=0,
                column=1,
                sticky="nsew",
            )
            self.frame.after_idle(self._finish_documents_transition)

            if target_workspace:
                self.frame.after_idle(
                    lambda key=target_workspace: self._open_target_workspace(key)
                )

    def _finish_documents_transition(self) -> None:
        self._documents_transitioning = False

    def _wrap_document_view_navigation(self, view, project) -> None:
        """Enregistre automatiquement le dernier bureau réellement ouvert."""

        for bureau_key, method_name in self.DOCUMENT_VIEW_METHODS.items():
            original = getattr(view, method_name, None)
            if not callable(original):
                continue

            def wrapped(
                *args,
                _original=original,
                _bureau_key=bureau_key,
                **kwargs,
            ):
                self._record_project_activity(project, _bureau_key)
                return _original(*args, **kwargs)

            setattr(view, method_name, wrapped)

    def _open_target_workspace(self, workspace_key: str) -> None:
        if workspace_key == "centre":
            return

        view = self._document_view
        if view is None:
            return

        method_name = self.DOCUMENT_VIEW_METHODS.get(workspace_key)
        if not method_name:
            return

        method = getattr(view, method_name, None)
        if callable(method):
            method()

    def show_document(
        self,
        document_info,
    ) -> None:
        self._destroy_cleanup_view()
        self._set_navigation_visible(True)
        self.clear()

        self.application.document_manager.load_document(
            document_info["nom"],
        )

        DocumentEditorView(
            self.frame,
            self.application,
            on_back=self.back_to_documents,
        ).show()

    def back_to_documents(self) -> None:
        if self.current_project is not None:
            self.show_documents(self.current_project)

    # ==========================================================
    # Nettoyage du projet
    # ==========================================================

    def show_project_cleanup(self) -> None:
        if (
            self.current_project is None
            or self._cleanup_transitioning
        ):
            return

        self._cleanup_transitioning = True
        self.frame.grid_remove()

        try:
            self._set_navigation_visible(True)
            self.clear()

            self._cleanup_view = ProjectCleanupDialog(
                self.frame,
                self.current_project,
                on_close=self.back_to_documents,
            )

            self.frame.update_idletasks()

        finally:
            self.frame.grid(
                row=0,
                column=1,
                sticky="nsew",
            )
            self.frame.after_idle(
                self._finish_cleanup_transition
            )

    def _finish_cleanup_transition(self) -> None:
        self._cleanup_transitioning = False

    def _open_project_cleanup(self) -> None:
        self.show_project_cleanup()

    def _destroy_cleanup_view(self) -> None:
        view = self._cleanup_view

        if view is None:
            return

        try:
            view.on_close = None

            if view.winfo_exists():
                view.destroy()
        except Exception:
            pass

        self._cleanup_view = None

    def _close_cleanup_dialog(self) -> None:
        self._destroy_cleanup_view()

    # ==========================================================
    # Accueil : ouverture et accès directs
    # ==========================================================

    def _dashboard_new_project(self) -> None:
        window = getattr(self.application, "window", None)
        menu_bar = getattr(window, "menu", None)
        command = getattr(menu_bar, "new_project", None)

        if not callable(command):
            self._show_project_error(
                "La commande de création de projet est indisponible."
            )
            return

        command()

    def _dashboard_open_project(self) -> None:
        window = getattr(self.application, "window", None)
        menu_bar = getattr(window, "menu", None)
        command = getattr(menu_bar, "open_project", None)

        if not callable(command):
            self._show_project_error(
                "La commande d’ouverture de projet est indisponible."
            )
            return

        command()

    def _open_recent_project(self, project_data: dict) -> None:
        self._open_project_from_summary(project_data, target_workspace="centre")

    def _open_recent_workspace(
        self,
        project_data: dict,
        workspace_key: str,
    ) -> None:
        self._open_project_from_summary(
            project_data,
            target_workspace=workspace_key,
        )

    def _open_project_from_summary(
        self,
        project_data: dict,
        *,
        target_workspace: str,
    ) -> None:
        project_path = Path(
            str(project_data.get("chemin", ""))
        )

        if not project_path.is_dir():
            self._remove_recent_path(project_path)
            self._show_project_error(
                "Le dossier de ce projet récent est introuvable."
            )
            self.show_dashboard()
            return

        try:
            project = self.application.project_manager.open_project(
                str(project_path)
            )
            self.show_documents(
                project,
                target_workspace=target_workspace,
            )
        except Exception as exc:
            self._show_project_error(str(exc))

    def _show_project_error(self, message: str) -> None:
        from tkinter import messagebox

        messagebox.showerror(
            "Projet indisponible",
            message,
            parent=self.frame.winfo_toplevel(),
        )

    # ==========================================================
    # Projets récents et état automatique
    # ==========================================================

    @property
    def _recent_projects_file(self) -> Path:
        return Path.home() / ".pagemaitre" / "projets_recents.json"

    def _load_recent_projects(self) -> list[dict]:
        registry = self._read_recent_registry()
        refreshed: list[dict] = []

        for entry in registry:
            path = Path(str(entry.get("chemin", "")))
            if not path.is_dir():
                continue

            summary = self._summarize_project_path(path, entry)
            if summary is not None:
                refreshed.append(summary)

        refreshed.sort(
            key=lambda item: str(item.get("derniere_ouverture", "")),
            reverse=True,
        )
        refreshed = refreshed[: self.RECENT_PROJECTS_LIMIT]
        self._write_recent_registry(refreshed)
        return refreshed

    def _record_project_activity(
        self,
        project,
        bureau_key: str | None = None,
    ) -> None:
        project_root = getattr(project, "root", None)
        if project_root is None:
            return

        path = Path(project_root)
        registry = self._read_recent_registry()
        existing = next(
            (
                entry
                for entry in registry
                if self._same_path(entry.get("chemin", ""), path)
            ),
            {},
        )

        if bureau_key:
            existing = dict(existing)
            existing["dernier_bureau_key"] = bureau_key
            existing["dernier_bureau"] = self.BUREAU_LABELS.get(
                bureau_key,
                bureau_key,
            )

        summary = self._summarize_project_object(
            project,
            existing,
        )
        summary["derniere_ouverture"] = datetime.now().isoformat()

        remaining = [
            entry
            for entry in registry
            if not self._same_path(entry.get("chemin", ""), path)
        ]
        remaining.insert(0, summary)
        self._write_recent_registry(
            remaining[: self.RECENT_PROJECTS_LIMIT]
        )

    def _summarize_project_object(
        self,
        project,
        existing: dict,
    ) -> dict:
        path = Path(getattr(project, "root"))
        data = self._read_json(path / "projet.json")
        documents = list(getattr(project, "documents", []))
        if not documents:
            documents = list(data.get("documents", []))

        return self._build_project_summary(
            path=path,
            name=str(getattr(project, "name", "") or data.get("nom", "")),
            modification_date=str(
                getattr(project, "modification_date", "")
                or data.get("date_modification", "")
            ),
            documents=documents,
            project_data=data,
            existing=existing,
        )

    def _summarize_project_path(
        self,
        path: Path,
        existing: dict,
    ) -> dict | None:
        project_file = path / "projet.json"
        if not project_file.is_file():
            return None

        data = self._read_json(project_file)
        if not data:
            return None

        return self._build_project_summary(
            path=path,
            name=str(data.get("nom", path.name)),
            modification_date=str(data.get("date_modification", "")),
            documents=list(data.get("documents", [])),
            project_data=data,
            existing=existing,
        )

    def _build_project_summary(
        self,
        *,
        path: Path,
        name: str,
        modification_date: str,
        documents: list,
        project_data: dict,
        existing: dict,
    ) -> dict:
        pages = self._load_project_pages(path, documents)
        status, validated_count = self._derive_project_status(
            project_data,
            pages,
        )

        bureau_key = str(
            existing.get("dernier_bureau_key", "centre")
        )
        bureau_label = str(
            existing.get(
                "dernier_bureau",
                self.BUREAU_LABELS.get(bureau_key, "Centre du projet"),
            )
        )

        project_type = str(
            project_data.get("type_projet", "ouvrage_structure")
            or "ouvrage_structure"
        ).strip()

        return {
            "nom": name or path.name,
            "chemin": str(path),
            "type_projet": project_type,
            "date_modification": modification_date,
            "derniere_ouverture": str(
                existing.get("derniere_ouverture", modification_date)
            ),
            "statut": status,
            "pages": len(pages),
            "pages_validees": validated_count,
            "dernier_bureau_key": bureau_key,
            "dernier_bureau": bureau_label,
        }

    @staticmethod
    def _load_project_pages(
        project_root: Path,
        documents: list,
    ) -> list[dict]:
        pages: list[dict] = []

        for document in documents:
            if not isinstance(document, dict):
                continue

            name = str(document.get("nom", "")).strip()
            if not name:
                continue

            document_file = (
                project_root
                / "documents"
                / name
                / "document.json"
            )
            data = Workspace._read_json(document_file)
            raw_pages = data.get("pages", [])
            if isinstance(raw_pages, list):
                pages.extend(
                    dict(page)
                    for page in raw_pages
                    if isinstance(page, dict)
                )

        return pages

    @staticmethod
    def _derive_project_status(
        project_data: dict,
        pages: list[dict],
    ) -> tuple[str, int]:
        explicit_status = str(
            project_data.get("statut", "")
        ).strip().casefold()
        explicit_closed = bool(project_data.get("cloture", False))

        if explicit_closed or explicit_status in {
            "clôturé",
            "cloture",
            "clos",
            "terminé",
            "termine",
        }:
            validated = sum(
                1
                for page in pages
                if "valid" in str(page.get("etat", "")).casefold()
            )
            return "Clôturé", validated

        states = [
            str(page.get("etat", "Brouillon")).strip().casefold()
            for page in pages
        ]
        validated = sum(1 for state in states if "valid" in state)

        if any(
            marker in state
            for state in states
            for marker in (
                "à vérifier",
                "a verifier",
                "à valider",
                "a valider",
                "erreur",
            )
        ):
            return "À vérifier", validated

        if states and validated == len(states):
            return "Validé", validated

        return "En cours", validated

    def _read_recent_registry(self) -> list[dict]:
        data = self._read_json(self._recent_projects_file)
        values = data.get("projets", [])
        if not isinstance(values, list):
            return []
        return [dict(value) for value in values if isinstance(value, dict)]

    def _write_recent_registry(self, projects: list[dict]) -> None:
        path = self._recent_projects_file
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as file:
                json.dump(
                    {"version": "1.0", "projets": projects},
                    file,
                    ensure_ascii=False,
                    indent=2,
                )
        except OSError:
            pass

    def _remove_recent_path(self, path: Path) -> None:
        projects = [
            entry
            for entry in self._read_recent_registry()
            if not self._same_path(entry.get("chemin", ""), path)
        ]
        self._write_recent_registry(projects)

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return {}

        return data if isinstance(data, dict) else {}

    @staticmethod
    def _same_path(value, path: Path) -> bool:
        try:
            return Path(str(value)).resolve() == path.resolve()
        except (OSError, RuntimeError):
            return str(value) == str(path)

    # ==========================================================
    # Navigation latérale
    # ==========================================================

    def _set_navigation_visible(
        self,
        visible: bool,
    ) -> None:
        parent = self.frame.master

        if parent is None:
            return

        try:
            navigation_widgets = parent.grid_slaves(
                row=0,
                column=0,
            )
        except Exception:
            return

        for widget in navigation_widgets:
            if visible:
                widget.grid()
            else:
                widget.grid_remove()

    # ==========================================================
    # Fenêtre
    # ==========================================================

    def _set_window_project_title(self, project) -> None:
        try:
            self.frame.winfo_toplevel().title(
                f"Générateur de livres - {project.name}"
            )
        except Exception:
            pass

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"Workspace("
            f"current_project={self.current_project!r})"
        )
