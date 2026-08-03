from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Callable
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts


class CleanupDetailsDialog(ctk.CTkToplevel):
    """Affiche la liste détaillée des éléments détectés par le nettoyage."""

    def __init__(
        self,
        parent,
        title: str,
        project_root: Path,
        files: list[Path],
        dependency_text: str,
    ) -> None:
        super().__init__(parent)

        self.project_root = project_root
        self.files = list(files)
        self.dependency_text = dependency_text

        self.title(title)
        self.geometry("860x620")
        self.minsize(760, 520)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.close)

        self._build(title)
        self.after(80, self._center_window)

    def _build(self, title: str) -> None:
        container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=22,
        )
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            container,
            text=title,
            font=Fonts.TITLE,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
        )

        total_size = sum(
            self._safe_size(path)
            for path in self.files
        )

        ctk.CTkLabel(
            container,
            text=(
                f"{len(self.files)} fichier(s) — "
                f"{ProjectCleanupDialog._format_size(total_size)}"
            ),
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(4, 12),
        )

        body = ctk.CTkFrame(
            container,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color=Colors.BORDER,
        )
        body.grid(
            row=2,
            column=0,
            sticky="nsew",
        )
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            body,
            fg_color="#EEF2F6",
            corner_radius=8,
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(12, 6),
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Emplacement dans le projet",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=8,
        )

        ctk.CTkLabel(
            header,
            text="Taille",
            width=110,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=1,
            padx=(8, 12),
        )

        rows = ctk.CTkScrollableFrame(
            body,
            fg_color="transparent",
            corner_radius=0,
        )
        rows.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 8),
        )
        rows.grid_columnconfigure(0, weight=1)

        for index, path in enumerate(self.files):
            row = ctk.CTkFrame(
                rows,
                fg_color=(
                    "#FAFBFC"
                    if index % 2 == 0
                    else "#FFFFFF"
                ),
                corner_radius=6,
            )
            row.grid(
                row=index,
                column=0,
                sticky="ew",
                pady=2,
            )
            row.grid_columnconfigure(0, weight=1)

            try:
                relative = path.relative_to(
                    self.project_root
                ).as_posix()
            except ValueError:
                relative = str(path)

            ctk.CTkLabel(
                row,
                text=relative,
                font=Fonts.NORMAL,
                text_color=Colors.TEXT,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=12,
                pady=(8, 2),
            )

            ctk.CTkLabel(
                row,
                text=ProjectCleanupDialog._format_size(
                    self._safe_size(path)
                ),
                width=110,
                font=Fonts.NORMAL,
                text_color=Colors.TEXT_LIGHT,
            ).grid(
                row=0,
                column=1,
                padx=(8, 12),
                pady=(8, 2),
            )

            ctk.CTkLabel(
                row,
                text=f"Dépendance : {self.dependency_text}",
                font=Fonts.SMALL,
                text_color=Colors.TEXT_LIGHT,
                anchor="w",
            ).grid(
                row=1,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=12,
                pady=(0, 8),
            )

        footer = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        footer.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(14, 0),
        )
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            footer,
            text="Fermer",
            width=110,
            height=36,
            fg_color="#17365D",
            hover_color="#244B79",
            text_color="#FFFFFF",
            command=self.close,
        ).grid(
            row=0,
            column=1,
        )

    @staticmethod
    def _safe_size(path: Path) -> int:
        try:
            return path.stat().st_size
        except OSError:
            return 0

    def _center_window(self) -> None:
        self.update_idletasks()

        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(
            0,
            (parent.winfo_width() - self.winfo_width()) // 2,
        )
        y = parent.winfo_y() + max(
            0,
            (parent.winfo_height() - self.winfo_height()) // 2,
        )

        self.geometry(f"+{x}+{y}")

    def close(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass

        self.destroy()


class TrashContentsDialog(ctk.CTkToplevel):
    """Affiche tous les lots présents dans la corbeille interne."""

    def __init__(
        self,
        parent,
        project_root: Path,
        restore_callback: Callable[[Path], None],
    ) -> None:
        super().__init__(parent)

        self.project_root = project_root
        self.trash_root = project_root / "corbeille"
        self.restore_callback = restore_callback

        self.title("Contenu de la corbeille")
        self.geometry("900x640")
        self.minsize(780, 520)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.close)

        self._build()
        self.after(80, self._center_window)

    def _build(self) -> None:
        container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=22,
        )
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            container,
            text="Contenu de la corbeille",
            font=Fonts.TITLE,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
        )

        self.summary_var = tk.StringVar(value="Analyse en cours…")

        ctk.CTkLabel(
            container,
            textvariable=self.summary_var,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(4, 12),
        )

        self.rows = ctk.CTkScrollableFrame(
            container,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color=Colors.BORDER,
        )
        self.rows.grid(
            row=2,
            column=0,
            sticky="nsew",
        )
        self.rows.grid_columnconfigure(0, weight=1)

        footer = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        footer.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(14, 0),
        )
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            footer,
            text="Fermer",
            width=110,
            height=36,
            fg_color="#17365D",
            hover_color="#244B79",
            text_color="#FFFFFF",
            command=self.close,
        ).grid(
            row=0,
            column=1,
        )

        self.refresh()

    def refresh(self) -> None:
        for child in self.rows.winfo_children():
            child.destroy()

        batches = self._trash_batches()
        total_files = 0
        total_size = 0

        if not batches:
            ctk.CTkLabel(
                self.rows,
                text="La corbeille interne est vide.",
                font=Fonts.NORMAL,
                text_color=Colors.TEXT_LIGHT,
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=18,
                pady=28,
            )
            self.summary_var.set("Aucun lot restaurable.")
            return

        for row_index, batch in enumerate(batches):
            file_count, batch_size = (
                ProjectCleanupDialog._folder_stats(batch)
            )
            total_files += file_count
            total_size += batch_size

            row = ctk.CTkFrame(
                self.rows,
                fg_color=(
                    "#FAFBFC"
                    if row_index % 2 == 0
                    else "#FFFFFF"
                ),
                corner_radius=8,
            )
            row.grid(
                row=row_index,
                column=0,
                sticky="ew",
                padx=10,
                pady=4,
            )
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row,
                text=self._batch_label(batch),
                font=Fonts.H2,
                text_color=Colors.TEXT,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=12,
                pady=(10, 2),
            )

            ctk.CTkLabel(
                row,
                text=batch.name,
                font=Fonts.SMALL,
                text_color=Colors.TEXT_LIGHT,
                anchor="w",
            ).grid(
                row=1,
                column=0,
                sticky="ew",
                padx=12,
                pady=(0, 10),
            )

            ctk.CTkLabel(
                row,
                text=(
                    f"{file_count} fichier(s) — "
                    f"{ProjectCleanupDialog._format_size(batch_size)}"
                ),
                width=190,
                font=Fonts.NORMAL,
                text_color=Colors.TEXT,
            ).grid(
                row=0,
                column=1,
                rowspan=2,
                padx=10,
            )

            ctk.CTkButton(
                row,
                text="Restaurer ce lot",
                width=150,
                height=34,
                fg_color="#3B7A57",
                hover_color="#2F6246",
                text_color="#FFFFFF",
                command=lambda selected=batch: self._restore(selected),
            ).grid(
                row=0,
                column=2,
                rowspan=2,
                padx=(0, 12),
            )

        self.summary_var.set(
            f"{len(batches)} lot(s) — {total_files} fichier(s) — "
            f"{ProjectCleanupDialog._format_size(total_size)}"
        )

    def _restore(self, batch: Path) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass

        try:
            self.restore_callback(batch)
        finally:
            if self.winfo_exists():
                try:
                    self.grab_set()
                except tk.TclError:
                    pass
                self.refresh()

    def _trash_batches(self) -> list[Path]:
        if not self.trash_root.exists():
            return []

        try:
            batches = [
                item
                for item in self.trash_root.iterdir()
                if item.is_dir()
            ]
        except OSError:
            return []

        batches.sort(
            key=lambda item: item.name,
            reverse=True,
        )
        return batches

    @staticmethod
    def _batch_label(batch: Path) -> str:
        name = batch.name

        if name.startswith("cache_"):
            return "Cache"

        if name.startswith("visuels_temoins_"):
            return "Visuels témoins"

        if name.startswith("ressources_historique_"):
            return "Ressources liées à l’historique"

        if name.startswith("ressources_graphiques_"):
            return "Ressources graphiques"

        return "Lot non identifié"

    def _center_window(self) -> None:
        self.update_idletasks()

        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(
            0,
            (parent.winfo_width() - self.winfo_width()) // 2,
        )
        y = parent.winfo_y() + max(
            0,
            (parent.winfo_height() - self.winfo_height()) // 2,
        )

        self.geometry(f"+{x}+{y}")

    def close(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass

        self.destroy()


class ProjectCleanupDialog(ctk.CTkToplevel):
    """Analyse le stockage du projet actuellement ouvert."""

    CATEGORY_FOLDERS = (
        ("Documents", "documents"),
        ("Ressources", "ressources"),
        ("Modèles", "modeles"),
        ("Contenus", "contenus"),
        ("Productions", "productions"),
        ("Exports", "exports"),
        ("Cache", "cache"),
        ("Corbeille interne", "corbeille"),
    )

    def __init__(
        self,
        parent,
        project,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent)

        self.project = project
        self.on_close = on_close
        self._closed = False
        self._rows: dict[str, tuple[ctk.CTkLabel, ctk.CTkLabel]] = {}
        self._cache_file_count = 0
        self._cache_size = 0
        self._latest_trash_cache: Path | None = None
        self._trash_file_count = 0
        self._trash_size = 0
        self._unused_visual_references: list[dict] = []
        self._unused_visual_size = 0
        self._latest_trash_visuals: Path | None = None
        self._unused_graphic_resources: list[Path] = []
        self._unused_graphic_size = 0
        self._latest_trash_graphics: Path | None = None
        self._history_only_graphic_resources: list[Path] = []
        self._history_only_graphic_size = 0
        self._latest_trash_history_graphics: Path | None = None

        self.title("Nettoyage de la base")
        self.geometry("940x750")
        self.minsize(880, 690)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
        self.protocol("WM_DELETE_WINDOW", self.close)

        self._build()
        self.after(80, self._center_window)
        self.after(120, self.analyze)

    # ==========================================================
    # Construction
    # ==========================================================

    def _build(self) -> None:
        container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=22,
        )
        container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            container,
            text="Nettoyage de la base",
            font=Fonts.TITLE,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
        )

        project_name = str(
            getattr(self.project, "name", "")
            or "Projet sans nom"
        )
        root = self._project_root()

        ctk.CTkLabel(
            container,
            text=f"Projet analysé : {project_name}",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(8, 0),
        )

        ctk.CTkLabel(
            container,
            text=str(root) if root is not None else "Dossier indisponible",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(2, 14),
        )

        body = ctk.CTkFrame(
            container,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color=Colors.BORDER,
        )
        body.grid(
            row=3,
            column=0,
            sticky="ew",
        )
        body.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(
            body,
            fg_color="#EEF2F6",
            corner_radius=8,
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(12, 6),
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Zone du projet",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=8,
        )

        ctk.CTkLabel(
            header,
            text="Fichiers",
            width=90,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=1,
            padx=8,
        )

        ctk.CTkLabel(
            header,
            text="Espace occupé",
            width=130,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=2,
            padx=(8, 12),
        )

        rows = ctk.CTkFrame(
            body,
            fg_color="transparent",
            corner_radius=0,
        )
        rows.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 8),
        )
        rows.grid_columnconfigure(0, weight=1)

        for index, (label, folder_name) in enumerate(self.CATEGORY_FOLDERS):
            row = ctk.CTkFrame(
                rows,
                fg_color="#FAFBFC" if index % 2 == 0 else "#FFFFFF",
                corner_radius=6,
            )
            row.grid(
                row=index,
                column=0,
                sticky="ew",
                pady=2,
            )
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row,
                text=label,
                font=Fonts.NORMAL,
                text_color=Colors.TEXT,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=12,
                pady=9,
            )

            count_label = ctk.CTkLabel(
                row,
                text="—",
                width=90,
                font=Fonts.NORMAL,
                text_color=Colors.TEXT_LIGHT,
            )
            count_label.grid(
                row=0,
                column=1,
                padx=8,
            )

            size_label = ctk.CTkLabel(
                row,
                text="—",
                width=130,
                font=Fonts.NORMAL,
                text_color=Colors.TEXT_LIGHT,
            )
            size_label.grid(
                row=0,
                column=2,
                padx=(8, 12),
            )

            self._rows[folder_name] = (
                count_label,
                size_label,
            )

        summary = ctk.CTkFrame(
            container,
            fg_color="#EAF3FF",
            corner_radius=10,
            border_width=1,
            border_color="#B9D5F5",
        )
        summary.grid(
            row=4,
            column=0,
            sticky="ew",
            pady=(14, 0),
        )
        summary.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            summary,
            text="Taille totale du projet",
            font=Fonts.H2,
            text_color="#17365D",
            anchor="w",
        ).grid(
            row=0,
            column=0,
            padx=14,
            pady=(12, 5),
        )

        self.total_var = tk.StringVar(value="Analyse en cours…")

        ctk.CTkLabel(
            summary,
            textvariable=self.total_var,
            font=Fonts.H2,
            text_color="#17365D",
            anchor="e",
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=14,
            pady=(12, 5),
        )

        ctk.CTkLabel(
            summary,
            text="Cache pouvant être isolé",
            font=Fonts.NORMAL,
            text_color="#17365D",
            anchor="w",
        ).grid(
            row=1,
            column=0,
            padx=14,
            pady=(0, 12),
        )

        self.cache_recoverable_var = tk.StringVar(value="—")

        ctk.CTkLabel(
            summary,
            textvariable=self.cache_recoverable_var,
            font=Fonts.NORMAL,
            text_color="#17365D",
            anchor="e",
        ).grid(
            row=1,
            column=1,
            sticky="e",
            padx=14,
            pady=(0, 5),
        )

        ctk.CTkLabel(
            summary,
            text="Visuels témoins inutilisés",
            font=Fonts.NORMAL,
            text_color="#17365D",
            anchor="w",
        ).grid(
            row=2,
            column=0,
            padx=14,
            pady=(0, 12),
        )

        self.unused_visuals_var = tk.StringVar(value="Analyse en cours…")

        ctk.CTkLabel(
            summary,
            textvariable=self.unused_visuals_var,
            font=Fonts.NORMAL,
            text_color="#17365D",
            anchor="e",
        ).grid(
            row=2,
            column=1,
            sticky="e",
            padx=14,
            pady=(0, 5),
        )

        ctk.CTkLabel(
            summary,
            text="Ressources graphiques non référencées",
            font=Fonts.NORMAL,
            text_color="#17365D",
            anchor="w",
        ).grid(
            row=3,
            column=0,
            padx=14,
            pady=(0, 12),
        )

        self.unused_graphics_var = tk.StringVar(
            value="Analyse en cours…"
        )

        ctk.CTkLabel(
            summary,
            textvariable=self.unused_graphics_var,
            font=Fonts.NORMAL,
            text_color="#17365D",
            anchor="e",
        ).grid(
            row=3,
            column=1,
            sticky="e",
            padx=14,
            pady=(0, 5),
        )

        ctk.CTkLabel(
            summary,
            text="Ressources conservées seulement par l’historique",
            font=Fonts.NORMAL,
            text_color="#8A5A00",
            anchor="w",
        ).grid(
            row=4,
            column=0,
            padx=14,
            pady=(0, 12),
        )

        self.history_only_graphics_var = tk.StringVar(
            value="Analyse en cours…"
        )

        ctk.CTkLabel(
            summary,
            textvariable=self.history_only_graphics_var,
            font=Fonts.NORMAL,
            text_color="#8A5A00",
            anchor="e",
        ).grid(
            row=4,
            column=1,
            sticky="e",
            padx=14,
            pady=(0, 12),
        )

        footer = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        footer.grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(14, 0),
        )
        footer.grid_columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(
            value="Le cache peut être déplacé dans la corbeille interne sans suppression définitive."
        )

        ctk.CTkLabel(
            footer,
            textvariable=self.status_var,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            columnspan=5,
            sticky="ew",
            pady=(0, 8),
        )

        self.move_cache_button = ctk.CTkButton(
            footer,
            text="Mettre le cache à la corbeille",
            width=210,
            height=36,
            fg_color="#B76E00",
            hover_color="#945900",
            text_color="#FFFFFF",
            command=self.move_cache_to_trash,
            state="disabled",
        )
        self.move_cache_button.grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 8),
        )

        self.restore_cache_button = ctk.CTkButton(
            footer,
            text="Restaurer le dernier cache",
            width=200,
            height=36,
            fg_color="#3B7A57",
            hover_color="#2F6246",
            text_color="#FFFFFF",
            command=self.restore_latest_cache,
            state="disabled",
        )
        self.restore_cache_button.grid(
            row=1,
            column=1,
            padx=(0, 8),
        )

        self.empty_trash_button = ctk.CTkButton(
            footer,
            text="Vider la corbeille",
            width=160,
            height=36,
            fg_color="#B42318",
            hover_color="#8F1C14",
            text_color="#FFFFFF",
            command=self.empty_trash,
            state="disabled",
        )
        self.empty_trash_button.grid(
            row=1,
            column=2,
            padx=(0, 8),
        )

        self.view_trash_button = ctk.CTkButton(
            footer,
            text="Voir le contenu de la corbeille",
            width=250,
            height=36,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self.show_trash_contents,
            state="disabled",
        )
        self.view_trash_button.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 0),
        )

        ctk.CTkButton(
            footer,
            text="Actualiser",
            width=110,
            height=36,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self.analyze,
        ).grid(
            row=1,
            column=3,
            padx=(0, 8),
        )

        ctk.CTkButton(
            footer,
            text="Fermer",
            width=110,
            height=36,
            fg_color="#17365D",
            hover_color="#244B79",
            text_color="#FFFFFF",
            command=self.close,
        ).grid(
            row=1,
            column=4,
        )

        self.move_unused_visuals_button = ctk.CTkButton(
            footer,
            text="Mettre les visuels inutilisés à la corbeille",
            width=320,
            height=36,
            fg_color="#7B61D1",
            hover_color="#624DB0",
            text_color="#FFFFFF",
            command=self.move_unused_visuals_to_trash,
            state="disabled",
        )
        self.move_unused_visuals_button.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 0),
        )

        self.restore_visuals_button = ctk.CTkButton(
            footer,
            text="Restaurer les derniers visuels",
            width=250,
            height=36,
            fg_color="#3B7A57",
            hover_color="#2F6246",
            text_color="#FFFFFF",
            command=self.restore_latest_visuals,
            state="disabled",
        )
        self.restore_visuals_button.grid(
            row=2,
            column=2,
            columnspan=2,
            sticky="w",
            padx=(8, 0),
            pady=(8, 0),
        )

        self.move_unused_graphics_button = ctk.CTkButton(
            footer,
            text="Mettre les ressources graphiques à la corbeille",
            width=360,
            height=36,
            fg_color="#7B61D1",
            hover_color="#624DB0",
            text_color="#FFFFFF",
            command=self.move_unused_graphics_to_trash,
            state="disabled",
        )
        self.move_unused_graphics_button.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(8, 0),
        )

        self.restore_graphics_button = ctk.CTkButton(
            footer,
            text="Restaurer les dernières ressources",
            width=270,
            height=36,
            fg_color="#3B7A57",
            hover_color="#2F6246",
            text_color="#FFFFFF",
            command=self.restore_latest_graphics,
            state="disabled",
        )
        self.restore_graphics_button.grid(
            row=3,
            column=3,
            columnspan=2,
            sticky="e",
            padx=(8, 0),
            pady=(8, 0),
        )

        self.show_graphics_details_button = ctk.CTkButton(
            footer,
            text="Voir le détail des ressources",
            width=240,
            height=36,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self.show_unused_graphics_details,
            state="disabled",
        )
        self.show_graphics_details_button.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 0),
        )

        self.show_visuals_details_button = ctk.CTkButton(
            footer,
            text="Voir le détail des visuels",
            width=220,
            height=36,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self.show_unused_visuals_details,
            state="disabled",
        )
        self.show_visuals_details_button.grid(
            row=4,
            column=2,
            columnspan=2,
            sticky="w",
            padx=(8, 0),
            pady=(8, 0),
        )

        self.show_cache_details_button = ctk.CTkButton(
            footer,
            text="Voir le détail du cache",
            width=200,
            height=36,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self.show_cache_details,
            state="disabled",
        )
        self.show_cache_details_button.grid(
            row=4,
            column=4,
            sticky="e",
            padx=(8, 0),
            pady=(8, 0),
        )

        self.show_history_graphics_details_button = ctk.CTkButton(
            footer,
            text="Voir les ressources liées à l’historique",
            width=290,
            height=36,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self.show_history_only_graphics_details,
            state="disabled",
        )
        self.show_history_graphics_details_button.grid(
            row=5,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(8, 0),
        )

        self.move_history_graphics_button = ctk.CTkButton(
            footer,
            text="Mettre les ressources historiques à la corbeille",
            width=350,
            height=36,
            fg_color="#B76E00",
            hover_color="#945900",
            text_color="#FFFFFF",
            command=self.move_history_only_graphics_to_trash,
            state="disabled",
        )
        self.move_history_graphics_button.grid(
            row=5,
            column=3,
            columnspan=2,
            sticky="e",
            padx=(8, 0),
            pady=(8, 0),
        )

        self.restore_history_graphics_button = ctk.CTkButton(
            footer,
            text="Restaurer les ressources historiques",
            width=280,
            height=36,
            fg_color="#3B7A57",
            hover_color="#2F6246",
            text_color="#FFFFFF",
            command=self.restore_latest_history_graphics,
            state="disabled",
        )
        self.restore_history_graphics_button.grid(
            row=6,
            column=3,
            columnspan=2,
            sticky="e",
            padx=(8, 0),
            pady=(8, 0),
        )

    # ==========================================================
    # Analyse
    # ==========================================================

    def analyze(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            self.total_var.set("Dossier indisponible")
            return

        total_size = 0

        for _, folder_name in self.CATEGORY_FOLDERS:
            folder = root / folder_name
            file_count, folder_size = self._folder_stats(folder)
            total_size += folder_size

            labels = self._rows.get(folder_name)

            if labels is None:
                continue

            count_label, size_label = labels
            count_label.configure(
                text=str(file_count),
                text_color=Colors.TEXT,
            )
            size_label.configure(
                text=self._format_size(folder_size),
                text_color=Colors.TEXT,
            )

        root_file_size = 0

        try:
            for item in root.iterdir():
                if item.is_file():
                    try:
                        root_file_size += item.stat().st_size
                    except OSError:
                        pass
        except OSError:
            pass

        total_size += root_file_size
        self.total_var.set(self._format_size(total_size))

        self._cache_file_count, self._cache_size = self._folder_stats(
            root / "cache"
        )
        self.cache_recoverable_var.set(
            f"{self._cache_file_count} fichier(s) — {self._format_size(self._cache_size)}"
        )
        cache_state = (
            "normal"
            if self._cache_file_count > 0
            else "disabled"
        )
        self.move_cache_button.configure(
            state=cache_state
        )
        self.show_cache_details_button.configure(
            state=cache_state
        )

        self._latest_trash_cache = self._find_latest_trash_cache(root)
        self.restore_cache_button.configure(
            state="normal" if self._latest_trash_cache is not None else "disabled"
        )

        self._trash_file_count, self._trash_size = self._folder_stats(
            root / "corbeille"
        )
        trash_state = (
            "normal"
            if self._trash_file_count > 0
            else "disabled"
        )
        self.empty_trash_button.configure(
            state=trash_state
        )
        self.view_trash_button.configure(
            state=trash_state
        )

        (
            self._unused_visual_references,
            self._unused_visual_size,
        ) = self._find_unused_visual_references(root)
        self.unused_visuals_var.set(
            f"{len(self._unused_visual_references)} fichier(s) — "
            f"{self._format_size(self._unused_visual_size)}"
        )
        visuals_state = (
            "normal"
            if self._unused_visual_references
            else "disabled"
        )
        self.move_unused_visuals_button.configure(
            state=visuals_state
        )
        self.show_visuals_details_button.configure(
            state=visuals_state
        )

        self._latest_trash_visuals = self._find_latest_trash_visuals(
            root
        )
        self.restore_visuals_button.configure(
            state=(
                "normal"
                if self._latest_trash_visuals is not None
                else "disabled"
            )
        )

        (
            self._unused_graphic_resources,
            self._unused_graphic_size,
        ) = self._find_unused_graphic_resources(root)
        self.unused_graphics_var.set(
            f"{len(self._unused_graphic_resources)} fichier(s) — "
            f"{self._format_size(self._unused_graphic_size)}"
        )
        graphics_state = (
            "normal"
            if self._unused_graphic_resources
            else "disabled"
        )
        self.move_unused_graphics_button.configure(
            state=graphics_state
        )
        self.show_graphics_details_button.configure(
            state=graphics_state
        )

        (
            self._history_only_graphic_resources,
            self._history_only_graphic_size,
        ) = self._find_history_only_graphic_resources(root)
        self.history_only_graphics_var.set(
            f"{len(self._history_only_graphic_resources)} fichier(s) — "
            f"{self._format_size(self._history_only_graphic_size)}"
        )
        history_state = (
            "normal"
            if self._history_only_graphic_resources
            else "disabled"
        )
        self.show_history_graphics_details_button.configure(
            state=history_state
        )
        self.move_history_graphics_button.configure(
            state=history_state
        )

        self._latest_trash_history_graphics = (
            self._find_latest_trash_history_graphics(root)
        )
        self.restore_history_graphics_button.configure(
            state=(
                "normal"
                if self._latest_trash_history_graphics is not None
                else "disabled"
            )
        )

        self._latest_trash_graphics = self._find_latest_trash_graphics(
            root
        )
        self.restore_graphics_button.configure(
            state=(
                "normal"
                if self._latest_trash_graphics is not None
                else "disabled"
            )
        )

        if self._cache_file_count > 0:
            self.status_var.set(
                "Le cache peut être déplacé dans la corbeille interne sans suppression définitive."
            )
        elif self._latest_trash_cache is not None:
            self.status_var.set(
                "Le cache est vide. Le dernier lot placé dans la corbeille peut être restauré."
            )
        elif self._trash_file_count > 0:
            self.status_var.set(
                f"La corbeille contient {self._trash_file_count} fichier(s), soit "
                f"{self._format_size(self._trash_size)}."
            )
        elif self._unused_visual_references:
            self.status_var.set(
                f"{len(self._unused_visual_references)} visuel(s) témoin(s) ne sont associés "
                "à aucune page du projet."
            )
        elif self._latest_trash_visuals is not None:
            self.status_var.set(
                "Le dernier lot de visuels témoins placé dans la corbeille "
                "peut être restauré."
            )
        elif self._unused_graphic_resources:
            self.status_var.set(
                f"{len(self._unused_graphic_resources)} ressource(s) graphique(s) "
                "ne sont référencées dans aucun document actif."
            )
        elif self._latest_trash_graphics is not None:
            self.status_var.set(
                "Le dernier lot de ressources graphiques placé dans la "
                "corbeille peut être restauré."
            )
        elif self._history_only_graphic_resources:
            self.status_var.set(
                f"{len(self._history_only_graphic_resources)} ressource(s) "
                "graphique(s) ne sont utilisées que par l’historique."
            )
        elif self._latest_trash_history_graphics is not None:
            self.status_var.set(
                "Le dernier lot de ressources liées à l’historique "
                "peut être restauré."
            )
        else:
            self.status_var.set(
                "Le cache et la corbeille sont vides. "
                "Aucune ressource graphique inutilisée détectée."
            )

    def show_cache_details(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        cache_folder = root / "cache"
        files = self._list_files(cache_folder)

        if not files:
            messagebox.showinfo(
                "Cache vide",
                "Aucun fichier de cache n’est présent.",
                parent=self,
            )
            self.analyze()
            return

        CleanupDetailsDialog(
            parent=self,
            title="Fichiers du cache",
            project_root=root,
            files=files,
            dependency_text=(
                "fichier temporaire — aucune dépendance durable attendue"
            ),
        )

    @staticmethod
    def _list_files(folder: Path) -> list[Path]:
        if not folder.exists():
            return []

        try:
            files = [
                item
                for item in folder.rglob("*")
                if item.is_file()
            ]
        except OSError:
            return []

        files.sort(
            key=lambda path: str(path).casefold()
        )

        return files

    def move_cache_to_trash(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        cache_folder = root / "cache"
        file_count, cache_size = self._folder_stats(cache_folder)

        if file_count == 0:
            messagebox.showinfo(
                "Cache vide",
                "Aucun fichier de cache n’est à déplacer.",
                parent=self,
            )
            self.analyze()
            return

        confirmed = messagebox.askyesno(
            "Mettre le cache à la corbeille",
            (
                f"{file_count} fichier(s), soit {self._format_size(cache_size)}, "
                "seront déplacés dans la corbeille interne du projet.\n\n"
                "Ils ne seront pas supprimés définitivement."
            ),
            parent=self,
        )

        if not confirmed:
            return

        trash_root = root / "corbeille"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = trash_root / f"cache_{timestamp}"
        suffix = 1

        while destination.exists():
            destination = trash_root / f"cache_{timestamp}_{suffix}"
            suffix += 1

        destination.mkdir(parents=True, exist_ok=False)

        try:
            for item in list(cache_folder.iterdir()):
                shutil.move(str(item), str(destination / item.name))
        except Exception as exc:
            messagebox.showerror(
                "Déplacement incomplet",
                (
                    "Une partie du cache a pu être déplacée dans la corbeille, "
                    f"mais l’opération n’a pas pu se terminer.\n\n{exc}"
                ),
                parent=self,
            )
            cache_folder.mkdir(parents=True, exist_ok=True)
            self.analyze()
            return

        cache_folder.mkdir(parents=True, exist_ok=True)
        self.analyze()
        self.status_var.set(
            f"Cache déplacé dans : {destination.name}"
        )

        messagebox.showinfo(
            "Cache mis à la corbeille",
            (
                f"{file_count} fichier(s) ont été déplacés dans la corbeille interne.\n"
                "Aucune suppression définitive n’a été effectuée."
            ),
            parent=self,
        )

    def restore_latest_cache(
        self,
        source: Path | None = None,
    ) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        if source is None:
            source = self._find_latest_trash_cache(root)

        if source is None:
            messagebox.showinfo(
                "Aucun cache à restaurer",
                "La corbeille interne ne contient aucun lot de cache.",
                parent=self,
            )
            self.analyze()
            return

        file_count, cache_size = self._folder_stats(source)

        confirmed = messagebox.askyesno(
            "Restaurer le cache",
            (
                f"Le lot {source.name} contient {file_count} fichier(s), "
                f"soit {self._format_size(cache_size)}.\n\n"
                "Son contenu sera replacé dans le dossier cache du projet."
            ),
            parent=self,
        )

        if not confirmed:
            return

        cache_folder = root / "cache"
        cache_folder.mkdir(parents=True, exist_ok=True)

        try:
            for item in list(source.iterdir()):
                destination = self._available_destination(
                    cache_folder / item.name
                )
                shutil.move(str(item), str(destination))

            source.rmdir()

        except Exception as exc:
            messagebox.showerror(
                "Restauration incomplète",
                (
                    "Une partie du cache a pu être restaurée, mais "
                    f"l’opération n’a pas pu se terminer.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"Cache restauré depuis : {source.name}"
        )

        messagebox.showinfo(
            "Cache restauré",
            f"{file_count} fichier(s) ont été replacés dans le cache du projet.",
            parent=self,
        )

    def show_trash_contents(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        trash_root = root / "corbeille"
        file_count, _ = self._folder_stats(trash_root)

        if file_count == 0:
            messagebox.showinfo(
                "Corbeille vide",
                "Aucun lot n’est présent dans la corbeille interne.",
                parent=self,
            )
            self.analyze()
            return

        TrashContentsDialog(
            parent=self,
            project_root=root,
            restore_callback=self.restore_trash_batch,
        )

    def restore_trash_batch(self, batch: Path) -> None:
        if not batch.exists() or not batch.is_dir():
            messagebox.showerror(
                "Lot indisponible",
                "Le lot sélectionné n’existe plus.",
                parent=self,
            )
            self.analyze()
            return

        name = batch.name

        if name.startswith("cache_"):
            self.restore_latest_cache(batch)
            return

        if name.startswith("visuels_temoins_"):
            self.restore_latest_visuals(batch)
            return

        if name.startswith("ressources_historique_"):
            self.restore_latest_history_graphics(batch)
            return

        if name.startswith("ressources_graphiques_"):
            self.restore_latest_graphics(batch)
            return

        messagebox.showerror(
            "Lot non reconnu",
            (
                "PageMaître ne connaît pas encore la méthode de "
                f"restauration du lot « {name} »."
            ),
            parent=self,
        )

    def empty_trash(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        trash_root = root / "corbeille"
        file_count, trash_size = self._folder_stats(trash_root)

        if file_count == 0:
            messagebox.showinfo(
                "Corbeille vide",
                "Aucun fichier n’est à supprimer définitivement.",
                parent=self,
            )
            self.analyze()
            return

        first_confirmation = messagebox.askyesno(
            "Vider la corbeille interne",
            (
                f"La corbeille contient {file_count} fichier(s), soit "
                f"{self._format_size(trash_size)}.\n\n"
                "Cette opération supprimera définitivement tous les éléments "
                "placés dans la corbeille de ce projet."
            ),
            parent=self,
        )

        if not first_confirmation:
            return

        final_confirmation = messagebox.askyesno(
            "Confirmation définitive",
            (
                "Les fichiers supprimés ne pourront plus être restaurés.\n\n"
                "Confirmer la suppression définitive ?"
            ),
            parent=self,
            icon="warning",
        )

        if not final_confirmation:
            return

        try:
            for item in list(trash_root.iterdir()):
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        except Exception as exc:
            messagebox.showerror(
                "Suppression incomplète",
                (
                    "Une partie de la corbeille a pu être supprimée, mais "
                    f"l’opération n’a pas pu se terminer.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        trash_root.mkdir(parents=True, exist_ok=True)
        self.analyze()
        self.status_var.set(
            f"Corbeille vidée : {self._format_size(trash_size)} récupérés."
        )

        messagebox.showinfo(
            "Corbeille vidée",
            (
                f"{file_count} fichier(s) ont été supprimés définitivement.\n"
                f"Espace récupéré : {self._format_size(trash_size)}."
            ),
            parent=self,
        )

    @staticmethod
    def _find_latest_trash_cache(root: Path) -> Path | None:
        trash_root = root / "corbeille"

        if not trash_root.exists():
            return None

        candidates = [
            item
            for item in trash_root.iterdir()
            if item.is_dir() and item.name.startswith("cache_")
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda item: item.name,
        )

    @staticmethod
    def _available_destination(destination: Path) -> Path:
        if not destination.exists():
            return destination

        stem = destination.stem
        suffix = destination.suffix
        index = 1

        while True:
            candidate = destination.with_name(
                f"{stem}_restaure_{index}{suffix}"
            )

            if not candidate.exists():
                return candidate

            index += 1

    def show_unused_visuals_details(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        unused, _ = self._find_unused_visual_references(root)

        if not unused:
            messagebox.showinfo(
                "Aucun visuel inutilisé",
                (
                    "Aucun visuel témoin sans association active "
                    "n’a été détecté."
                ),
                parent=self,
            )
            self.analyze()
            return

        files: list[Path] = []

        for summary in unused:
            relative_path = str(
                summary.get("fichier", "")
            ).strip()

            if relative_path:
                files.append(root / relative_path)

        if not files:
            messagebox.showerror(
                "Détail indisponible",
                (
                    "Les références inutilisées ne contiennent aucun "
                    "emplacement de fichier exploitable."
                ),
                parent=self,
            )
            return

        CleanupDetailsDialog(
            parent=self,
            title="Visuels témoins inutilisés",
            project_root=root,
            files=files,
            dependency_text="aucune page active associée",
        )

    def move_unused_visuals_to_trash(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        unused, unused_size = self._find_unused_visual_references(root)

        if not unused:
            messagebox.showinfo(
                "Aucun visuel inutilisé",
                "Tous les visuels témoins sont actuellement utilisés.",
                parent=self,
            )
            self.analyze()
            return

        confirmed = messagebox.askyesno(
            "Mettre les visuels inutilisés à la corbeille",
            (
                f"{len(unused)} visuel(s) témoin(s), soit "
                f"{self._format_size(unused_size)}, ne sont associés "
                "à aucune page.\n\n"
                "Ils seront déplacés dans la corbeille interne du projet "
                "et pourront être restaurés ultérieurement."
            ),
            parent=self,
        )

        if not confirmed:
            return

        trash_root = root / "corbeille"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch = trash_root / f"visuels_temoins_{timestamp}"
        suffix = 1

        while batch.exists():
            batch = trash_root / f"visuels_temoins_{timestamp}_{suffix}"
            suffix += 1

        batch.mkdir(parents=True, exist_ok=False)

        moved_files: list[tuple[Path, Path]] = []
        identifiers = {
            str(summary.get("identifiant", "")).strip()
            for summary in unused
            if str(summary.get("identifiant", "")).strip()
        }

        try:
            for summary in unused:
                relative_path = str(
                    summary.get("fichier", "")
                ).strip()

                if not relative_path:
                    continue

                source_path = root / relative_path

                if not source_path.is_file():
                    continue

                destination = batch / relative_path
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.move(
                    str(source_path),
                    str(destination),
                )
                moved_files.append(
                    (source_path, destination)
                )

            manifest = {
                "type": "visuels_temoins",
                "date": datetime.now().isoformat(),
                "projet": str(
                    getattr(self.project, "name", "")
                ),
                "elements": unused,
            }

            with (batch / "manifest.json").open(
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    manifest,
                    handle,
                    indent=4,
                    ensure_ascii=False,
                )

            original_index = list(
                getattr(
                    self.project,
                    "visual_references",
                    [],
                )
            )

            self.project.visual_references = [
                summary
                for summary in original_index
                if str(
                    summary.get("identifiant", "")
                ).strip() not in identifiers
            ]

            try:
                self.project.save()
            except Exception:
                self.project.visual_references = original_index
                raise

        except Exception as exc:
            for source_path, destination in reversed(moved_files):
                try:
                    source_path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_path),
                        )
                except Exception:
                    pass

            try:
                if batch.exists():
                    shutil.rmtree(batch)
            except Exception:
                pass

            messagebox.showerror(
                "Déplacement impossible",
                (
                    "Les visuels inutilisés n’ont pas pu être déplacés "
                    f"correctement.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(unused)} visuel(s) témoin(s) placés dans la corbeille."
        )

        messagebox.showinfo(
            "Visuels placés dans la corbeille",
            (
                f"{len(unused)} visuel(s) témoin(s) ont été retirés "
                "de la bibliothèque active.\n"
                "Aucune suppression définitive n’a été effectuée."
            ),
            parent=self,
        )

    def restore_latest_visuals(
        self,
        batch: Path | None = None,
    ) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        if batch is None:
            batch = self._find_latest_trash_visuals(root)

        if batch is None:
            messagebox.showinfo(
                "Aucun visuel à restaurer",
                "La corbeille ne contient aucun lot de visuels témoins.",
                parent=self,
            )
            self.analyze()
            return

        manifest_file = batch / "manifest.json"

        try:
            with manifest_file.open(
                "r",
                encoding="utf-8-sig",
            ) as handle:
                manifest = json.load(handle)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            messagebox.showerror(
                "Restauration impossible",
                (
                    "Le manifeste du lot de visuels est absent ou illisible.\n\n"
                    f"{exc}"
                ),
                parent=self,
            )
            return

        elements = manifest.get("elements", [])

        if not isinstance(elements, list) or not elements:
            messagebox.showerror(
                "Restauration impossible",
                "Le lot ne contient aucune référence exploitable.",
                parent=self,
            )
            return

        active_references = list(
            getattr(
                self.project,
                "visual_references",
                [],
            )
        )
        active_identifiers = {
            str(summary.get("identifiant", "")).strip()
            for summary in active_references
            if isinstance(summary, dict)
        }

        conflicts = [
            str(summary.get("identifiant", "")).strip()
            for summary in elements
            if (
                isinstance(summary, dict)
                and str(summary.get("identifiant", "")).strip()
                in active_identifiers
            )
        ]

        if conflicts:
            messagebox.showerror(
                "Restauration impossible",
                (
                    "Au moins un identifiant du lot existe déjà dans la "
                    "bibliothèque active. Aucun fichier n’a été déplacé."
                ),
                parent=self,
            )
            return

        confirmed = messagebox.askyesno(
            "Restaurer les visuels témoins",
            (
                f"{len(elements)} visuel(s) témoin(s) seront replacés "
                "dans la bibliothèque active du projet.\n\n"
                "Confirmer la restauration ?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        restored: list[tuple[Path, Path]] = []
        restored_summaries: list[dict] = []

        try:
            for summary in elements:
                if not isinstance(summary, dict):
                    continue

                restored_summary = dict(summary)
                relative_path = str(
                    restored_summary.get("fichier", "")
                ).strip()

                if not relative_path:
                    continue

                source_path = batch / relative_path

                if not source_path.is_file():
                    raise FileNotFoundError(
                        f"Fichier absent dans la corbeille : {relative_path}"
                    )

                destination = root / relative_path
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                if destination.exists():
                    destination = self._available_destination(
                        destination
                    )
                    restored_summary["fichier"] = (
                        destination.relative_to(root).as_posix()
                    )

                shutil.move(
                    str(source_path),
                    str(destination),
                )
                restored.append(
                    (source_path, destination)
                )
                restored_summaries.append(
                    restored_summary
                )

            self.project.visual_references = (
                active_references + restored_summaries
            )

            try:
                self.project.save()
            except Exception:
                self.project.visual_references = active_references
                raise

            shutil.rmtree(batch)

        except Exception as exc:
            self.project.visual_references = active_references

            for source_path, destination in reversed(restored):
                try:
                    source_path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_path),
                        )
                except Exception:
                    pass

            messagebox.showerror(
                "Restauration incomplète",
                (
                    "Les visuels n’ont pas pu être restaurés correctement.\n\n"
                    f"{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(restored_summaries)} visuel(s) témoin(s) restaurés."
        )

        messagebox.showinfo(
            "Visuels restaurés",
            (
                f"{len(restored_summaries)} visuel(s) témoin(s) ont été "
                "replacés dans la bibliothèque active."
            ),
            parent=self,
        )

    @staticmethod
    def _find_latest_trash_visuals(root: Path) -> Path | None:
        trash_root = root / "corbeille"

        if not trash_root.exists():
            return None

        candidates = [
            item
            for item in trash_root.iterdir()
            if (
                item.is_dir()
                and item.name.startswith("visuels_temoins_")
                and (item / "manifest.json").is_file()
            )
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda item: item.name,
        )

    def move_history_only_graphics_to_trash(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        files, _ = self._find_history_only_graphic_resources(root)

        if not files:
            messagebox.showinfo(
                "Aucune ressource historique",
                (
                    "Aucune ressource graphique utilisée seulement par "
                    "l’historique n’a été détectée."
                ),
                parent=self,
            )
            self.analyze()
            return

        first_confirmation = messagebox.askyesno(
            "Ressources nécessaires à l’historique",
            (
                f"{len(files)} fichier(s) ne sont plus utilisés par les "
                "pages actives, mais restent nécessaires pour certains "
                "états historiques.\n\n"
                "Après leur déplacement, ces anciens états pourront être "
                "incomplets tant que les fichiers ne seront pas restaurés.\n\n"
                "Continuer ?"
            ),
            parent=self,
        )

        if not first_confirmation:
            return

        second_confirmation = messagebox.askyesno(
            "Confirmer le déplacement",
            (
                "Les fichiers seront placés dans la corbeille interne du "
                "projet. Ils ne seront pas supprimés définitivement.\n\n"
                "Confirmer le déplacement des ressources historiques ?"
            ),
            parent=self,
        )

        if not second_confirmation:
            return

        trash_root = root / "corbeille"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch = trash_root / f"ressources_historique_{timestamp}"
        suffix = 1

        while batch.exists():
            batch = (
                trash_root
                / f"ressources_historique_{timestamp}_{suffix}"
            )
            suffix += 1

        batch.mkdir(
            parents=True,
            exist_ok=False,
        )

        moved_files: list[tuple[Path, Path]] = []
        relative_paths: list[str] = []

        original_index = list(
            getattr(
                self.project,
                "ressources",
                [],
            )
        )

        try:
            for source_path in files:
                relative_path = (
                    source_path.relative_to(root).as_posix()
                )
                destination = batch / relative_path
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.move(
                    str(source_path),
                    str(destination),
                )
                moved_files.append(
                    (source_path, destination)
                )
                relative_paths.append(relative_path)

            normalized_paths = {
                path.casefold()
                for path in relative_paths
            }

            retained_index = [
                summary
                for summary in original_index
                if not self._summary_references_paths(
                    summary,
                    normalized_paths,
                )
            ]

            manifest = {
                "type": "ressources_historique",
                "date": datetime.now().isoformat(),
                "projet": str(
                    getattr(self.project, "name", "")
                ),
                "fichiers": relative_paths,
                "index_retires": [
                    summary
                    for summary in original_index
                    if summary not in retained_index
                ],
            }

            with (batch / "manifest.json").open(
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    manifest,
                    handle,
                    indent=4,
                    ensure_ascii=False,
                )

            if retained_index != original_index:
                self.project.ressources = retained_index

                try:
                    self.project.save()
                except Exception:
                    self.project.ressources = original_index
                    raise

        except Exception as exc:
            self.project.ressources = original_index

            for source_path, destination in reversed(moved_files):
                try:
                    source_path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_path),
                        )
                except Exception:
                    pass

            try:
                if batch.exists():
                    shutil.rmtree(batch)
            except Exception:
                pass

            messagebox.showerror(
                "Déplacement impossible",
                (
                    "Les ressources liées à l’historique n’ont pas pu "
                    f"être déplacées correctement.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(relative_paths)} ressource(s) historique(s) "
            "placée(s) dans la corbeille."
        )

        messagebox.showinfo(
            "Ressources historiques déplacées",
            (
                f"{len(relative_paths)} fichier(s) ont été placés dans "
                "la corbeille interne.\n"
                "Ils restent restaurables."
            ),
            parent=self,
        )

    def restore_latest_history_graphics(
        self,
        batch: Path | None = None,
    ) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        if batch is None:
            batch = self._find_latest_trash_history_graphics(root)

        if batch is None:
            messagebox.showinfo(
                "Aucune ressource à restaurer",
                (
                    "La corbeille ne contient aucun lot de ressources "
                    "liées à l’historique."
                ),
                parent=self,
            )
            self.analyze()
            return

        manifest_file = batch / "manifest.json"

        try:
            with manifest_file.open(
                "r",
                encoding="utf-8-sig",
            ) as handle:
                manifest = json.load(handle)
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
        ) as exc:
            messagebox.showerror(
                "Restauration impossible",
                (
                    "Le manifeste du lot est absent ou illisible.\n\n"
                    f"{exc}"
                ),
                parent=self,
            )
            return

        files = manifest.get("fichiers", [])
        removed_index = manifest.get("index_retires", [])

        if not isinstance(files, list) or not files:
            messagebox.showerror(
                "Restauration impossible",
                "Le lot ne contient aucun fichier exploitable.",
                parent=self,
            )
            return

        confirmed = messagebox.askyesno(
            "Restaurer les ressources historiques",
            (
                f"{len(files)} fichier(s) seront replacés dans les "
                "bibliothèques graphiques du projet.\n\n"
                "Confirmer la restauration ?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        active_index = list(
            getattr(
                self.project,
                "ressources",
                [],
            )
        )
        restored: list[tuple[Path, Path]] = []
        path_mapping: dict[str, str] = {}

        try:
            for value in files:
                original_relative = str(value).strip()

                if not original_relative:
                    continue

                source_path = batch / original_relative

                if not source_path.is_file():
                    raise FileNotFoundError(
                        "Fichier absent dans la corbeille : "
                        f"{original_relative}"
                    )

                destination = root / original_relative
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                if destination.exists():
                    destination = self._available_destination(
                        destination
                    )

                restored_relative = (
                    destination.relative_to(root).as_posix()
                )
                path_mapping[original_relative] = restored_relative

                shutil.move(
                    str(source_path),
                    str(destination),
                )
                restored.append(
                    (source_path, destination)
                )

            restored_index = []

            if isinstance(removed_index, list):
                for summary in removed_index:
                    if not isinstance(summary, dict):
                        continue

                    restored_index.append(
                        self._replace_paths_in_value(
                            dict(summary),
                            path_mapping,
                        )
                    )

            combined_index = list(active_index)
            active_identifiers = {
                str(summary.get("identifiant", "")).strip()
                for summary in combined_index
                if isinstance(summary, dict)
            }

            for summary in restored_index:
                identifier = str(
                    summary.get("identifiant", "")
                ).strip()

                if identifier and identifier in active_identifiers:
                    continue

                combined_index.append(summary)

                if identifier:
                    active_identifiers.add(identifier)

            self.project.ressources = combined_index

            try:
                self.project.save()
            except Exception:
                self.project.ressources = active_index
                raise

            shutil.rmtree(batch)

        except Exception as exc:
            self.project.ressources = active_index

            for source_path, destination in reversed(restored):
                try:
                    source_path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_path),
                        )
                except Exception:
                    pass

            messagebox.showerror(
                "Restauration incomplète",
                (
                    "Les ressources historiques n’ont pas pu être "
                    f"restaurées correctement.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(restored)} ressource(s) historique(s) restaurée(s)."
        )

        messagebox.showinfo(
            "Ressources historiques restaurées",
            (
                f"{len(restored)} fichier(s) ont été replacés dans "
                "les bibliothèques graphiques du projet."
            ),
            parent=self,
        )

    @staticmethod
    def _find_latest_trash_history_graphics(
        root: Path,
    ) -> Path | None:
        trash_root = root / "corbeille"

        if not trash_root.exists():
            return None

        candidates = [
            item
            for item in trash_root.iterdir()
            if (
                item.is_dir()
                and item.name.startswith(
                    "ressources_historique_"
                )
                and (item / "manifest.json").is_file()
            )
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda item: item.name,
        )

    def show_history_only_graphics_details(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        files, _ = self._find_history_only_graphic_resources(root)

        if not files:
            messagebox.showinfo(
                "Aucune ressource historique",
                (
                    "Aucune ressource graphique utilisée seulement par "
                    "l’historique n’a été détectée."
                ),
                parent=self,
            )
            self.analyze()
            return

        CleanupDetailsDialog(
            parent=self,
            title="Ressources conservées seulement par l’historique",
            project_root=root,
            files=files,
            dependency_text=(
                "aucun usage actif — nécessaire seulement à un état historique"
            ),
        )

    def show_unused_graphics_details(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        unused, _ = self._find_unused_graphic_resources(root)

        if not unused:
            messagebox.showinfo(
                "Aucune ressource inutilisée",
                (
                    "Aucune ressource graphique non référencée "
                    "n’a été détectée."
                ),
                parent=self,
            )
            self.analyze()
            return

        CleanupDetailsDialog(
            parent=self,
            title="Ressources graphiques non référencées",
            project_root=root,
            files=unused,
            dependency_text="aucune référence active détectée",
        )

    def move_unused_graphics_to_trash(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        unused, unused_size = self._find_unused_graphic_resources(
            root
        )

        if not unused:
            messagebox.showinfo(
                "Aucune ressource inutilisée",
                (
                    "Toutes les ressources graphiques présentes sont "
                    "référencées dans le projet."
                ),
                parent=self,
            )
            self.analyze()
            return

        confirmed = messagebox.askyesno(
            "Mettre les ressources à la corbeille",
            (
                f"{len(unused)} fichier(s), soit "
                f"{self._format_size(unused_size)}, ne sont référencés "
                "dans aucun document actif.\n\n"
                "Ils seront déplacés dans la corbeille interne du projet "
                "et ne seront pas supprimés définitivement."
            ),
            parent=self,
        )

        if not confirmed:
            return

        trash_root = root / "corbeille"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch = trash_root / f"ressources_graphiques_{timestamp}"
        suffix = 1

        while batch.exists():
            batch = (
                trash_root
                / f"ressources_graphiques_{timestamp}_{suffix}"
            )
            suffix += 1

        batch.mkdir(
            parents=True,
            exist_ok=False,
        )

        moved_files: list[tuple[Path, Path]] = []
        relative_paths: list[str] = []

        original_index = list(
            getattr(
                self.project,
                "ressources",
                [],
            )
        )

        try:
            for source_path in unused:
                relative_path = (
                    source_path.relative_to(root).as_posix()
                )
                destination = batch / relative_path
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.move(
                    str(source_path),
                    str(destination),
                )
                moved_files.append(
                    (source_path, destination)
                )
                relative_paths.append(relative_path)

            normalized_paths = {
                path.casefold()
                for path in relative_paths
            }

            retained_index = [
                summary
                for summary in original_index
                if not self._summary_references_paths(
                    summary,
                    normalized_paths,
                )
            ]

            manifest = {
                "type": "ressources_graphiques",
                "date": datetime.now().isoformat(),
                "projet": str(
                    getattr(self.project, "name", "")
                ),
                "fichiers": relative_paths,
                "index_retires": [
                    summary
                    for summary in original_index
                    if summary not in retained_index
                ],
            }

            with (batch / "manifest.json").open(
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    manifest,
                    handle,
                    indent=4,
                    ensure_ascii=False,
                )

            if retained_index != original_index:
                self.project.ressources = retained_index

                try:
                    self.project.save()
                except Exception:
                    self.project.ressources = original_index
                    raise

        except Exception as exc:
            self.project.ressources = original_index

            for source_path, destination in reversed(moved_files):
                try:
                    source_path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_path),
                        )
                except Exception:
                    pass

            try:
                if batch.exists():
                    shutil.rmtree(batch)
            except Exception:
                pass

            messagebox.showerror(
                "Déplacement impossible",
                (
                    "Les ressources graphiques n’ont pas pu être "
                    f"déplacées correctement.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(relative_paths)} ressource(s) graphique(s) "
            "placée(s) dans la corbeille."
        )

        messagebox.showinfo(
            "Ressources placées dans la corbeille",
            (
                f"{len(relative_paths)} fichier(s) ont été retirés "
                "des bibliothèques actives.\n"
                "Aucune suppression définitive n’a été effectuée."
            ),
            parent=self,
        )

    @staticmethod
    def _summary_references_paths(
        summary,
        paths: set[str],
    ) -> bool:
        strings: set[str] = set()
        ProjectCleanupDialog._collect_string_references(
            summary,
            strings,
        )

        for value in strings:
            for path in paths:
                if (
                    value == path
                    or value.endswith("/" + path)
                ):
                    return True

        return False

    def restore_latest_graphics(
        self,
        batch: Path | None = None,
    ) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        if batch is None:
            batch = self._find_latest_trash_graphics(root)

        if batch is None:
            messagebox.showinfo(
                "Aucune ressource à restaurer",
                (
                    "La corbeille ne contient aucun lot de ressources "
                    "graphiques."
                ),
                parent=self,
            )
            self.analyze()
            return

        manifest_file = batch / "manifest.json"

        try:
            with manifest_file.open(
                "r",
                encoding="utf-8-sig",
            ) as handle:
                manifest = json.load(handle)
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
        ) as exc:
            messagebox.showerror(
                "Restauration impossible",
                (
                    "Le manifeste du lot est absent ou illisible.\n\n"
                    f"{exc}"
                ),
                parent=self,
            )
            return

        files = manifest.get("fichiers", [])
        removed_index = manifest.get("index_retires", [])

        if not isinstance(files, list) or not files:
            messagebox.showerror(
                "Restauration impossible",
                "Le lot ne contient aucun fichier exploitable.",
                parent=self,
            )
            return

        confirmed = messagebox.askyesno(
            "Restaurer les ressources graphiques",
            (
                f"{len(files)} fichier(s) seront replacés dans les "
                "bibliothèques graphiques du projet.\n\n"
                "Confirmer la restauration ?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        active_index = list(
            getattr(
                self.project,
                "ressources",
                [],
            )
        )
        restored: list[tuple[Path, Path]] = []
        path_mapping: dict[str, str] = {}

        try:
            for value in files:
                original_relative = str(value).strip()

                if not original_relative:
                    continue

                source_path = batch / original_relative

                if not source_path.is_file():
                    raise FileNotFoundError(
                        "Fichier absent dans la corbeille : "
                        f"{original_relative}"
                    )

                destination = root / original_relative
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                if destination.exists():
                    destination = self._available_destination(
                        destination
                    )

                restored_relative = (
                    destination.relative_to(root).as_posix()
                )
                path_mapping[original_relative] = restored_relative

                shutil.move(
                    str(source_path),
                    str(destination),
                )
                restored.append(
                    (source_path, destination)
                )

            restored_index = []

            if isinstance(removed_index, list):
                for summary in removed_index:
                    if not isinstance(summary, dict):
                        continue

                    restored_index.append(
                        self._replace_paths_in_value(
                            dict(summary),
                            path_mapping,
                        )
                    )

            combined_index = list(active_index)
            active_identifiers = {
                str(summary.get("identifiant", "")).strip()
                for summary in combined_index
                if isinstance(summary, dict)
            }

            for summary in restored_index:
                identifier = str(
                    summary.get("identifiant", "")
                ).strip()

                if identifier and identifier in active_identifiers:
                    continue

                combined_index.append(summary)

                if identifier:
                    active_identifiers.add(identifier)

            self.project.ressources = combined_index

            try:
                self.project.save()
            except Exception:
                self.project.ressources = active_index
                raise

            shutil.rmtree(batch)

        except Exception as exc:
            self.project.ressources = active_index

            for source_path, destination in reversed(restored):
                try:
                    source_path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_path),
                        )
                except Exception:
                    pass

            messagebox.showerror(
                "Restauration incomplète",
                (
                    "Les ressources n’ont pas pu être restaurées "
                    f"correctement.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(restored)} ressource(s) graphique(s) restaurée(s)."
        )

        messagebox.showinfo(
            "Ressources restaurées",
            (
                f"{len(restored)} fichier(s) ont été replacés dans "
                "les bibliothèques graphiques du projet."
            ),
            parent=self,
        )

    @staticmethod
    def _find_latest_trash_graphics(root: Path) -> Path | None:
        trash_root = root / "corbeille"

        if not trash_root.exists():
            return None

        candidates = [
            item
            for item in trash_root.iterdir()
            if (
                item.is_dir()
                and item.name.startswith(
                    "ressources_graphiques_"
                )
                and (item / "manifest.json").is_file()
            )
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda item: item.name,
        )

    @staticmethod
    def _replace_paths_in_value(
        value,
        path_mapping: dict[str, str],
    ):
        if isinstance(value, str):
            normalized = value.replace("\\", "/")

            for old_path, new_path in path_mapping.items():
                if normalized == old_path:
                    return new_path

                suffix = "/" + old_path

                if normalized.endswith(suffix):
                    prefix = normalized[:-len(old_path)]
                    return prefix + new_path

            return value

        if isinstance(value, dict):
            return {
                key: ProjectCleanupDialog._replace_paths_in_value(
                    child,
                    path_mapping,
                )
                for key, child in value.items()
            }

        if isinstance(value, list):
            return [
                ProjectCleanupDialog._replace_paths_in_value(
                    child,
                    path_mapping,
                )
                for child in value
            ]

        return value

    def _find_history_only_graphic_resources(
        self,
        root: Path,
    ) -> tuple[list[Path], int]:
        active_references, history_references = (
            self._collect_active_and_history_path_references(root)
        )
        files: list[Path] = []
        total_size = 0

        for candidate in self._graphic_resource_files(root):
            active = self._path_matches_references(
                candidate,
                root,
                active_references,
            )
            historical = self._path_matches_references(
                candidate,
                root,
                history_references,
            )

            if active or not historical:
                continue

            files.append(candidate)

            try:
                total_size += candidate.stat().st_size
            except OSError:
                pass

        files.sort(
            key=lambda path: str(path).casefold()
        )

        return files, total_size

    @staticmethod
    def _graphic_resource_files(root: Path) -> list[Path]:
        folders = (
            root / "ressources" / "images",
            root / "ressources" / "illustrations",
            root / "ressources" / "icones",
            root / "ressources" / "logos",
        )
        files: list[Path] = []

        for folder in folders:
            if not folder.exists():
                continue

            try:
                files.extend(
                    item
                    for item in folder.rglob("*")
                    if item.is_file()
                )
            except OSError:
                continue

        return files

    @staticmethod
    def _path_matches_references(
        candidate: Path,
        root: Path,
        references: set[str],
    ) -> bool:
        try:
            relative = candidate.relative_to(root).as_posix().casefold()
        except ValueError:
            return False

        try:
            absolute = str(candidate.resolve()).replace(
                "\\",
                "/",
            ).casefold()
        except OSError:
            absolute = str(candidate).replace(
                "\\",
                "/",
            ).casefold()

        return any(
            reference == relative
            or reference == absolute
            or reference.endswith("/" + relative)
            for reference in references
        )

    def _find_unused_graphic_resources(
        self,
        root: Path,
    ) -> tuple[list[Path], int]:
        resource_folders = (
            root / "ressources" / "images",
            root / "ressources" / "illustrations",
            root / "ressources" / "icones",
            root / "ressources" / "logos",
        )

        references = self._collect_project_path_references(root)
        unused: list[Path] = []
        total_size = 0

        for folder in resource_folders:
            if not folder.exists():
                continue

            try:
                candidates = folder.rglob("*")
            except OSError:
                continue

            for candidate in candidates:
                try:
                    if not candidate.is_file():
                        continue
                except OSError:
                    continue

                try:
                    relative_path = candidate.relative_to(root).as_posix()
                except ValueError:
                    continue

                normalized_relative = relative_path.casefold()
                absolute_path = str(candidate.resolve()).replace(
                    "\\",
                    "/",
                ).casefold()

                is_referenced = any(
                    reference == normalized_relative
                    or reference == absolute_path
                    or reference.endswith(
                        "/" + normalized_relative
                    )
                    for reference in references
                )

                if is_referenced:
                    continue

                unused.append(candidate)

                try:
                    total_size += candidate.stat().st_size
                except OSError:
                    pass

        unused.sort(
            key=lambda path: str(path).casefold()
        )

        return unused, total_size

    def _collect_project_path_references(
        self,
        root: Path,
    ) -> set[str]:
        active, history = (
            self._collect_active_and_history_path_references(root)
        )
        return active | history

    def _collect_active_and_history_path_references(
        self,
        root: Path,
    ) -> tuple[set[str], set[str]]:
        active_references: set[str] = set()
        history_references: set[str] = set()
        search_roots = (
            root / "projet.json",
            root / "documents",
            root / "modeles",
            root / "contenus",
            root / "productions",
        )
        history_folder_names = {
            "historique",
            "history",
            "versions",
            "archives",
        }

        for search_root in search_roots:
            if search_root.is_file():
                json_files = [search_root]
            elif search_root.exists():
                try:
                    json_files = list(
                        search_root.rglob("*.json")
                    )
                except OSError:
                    json_files = []
            else:
                json_files = []

            for json_file in json_files:
                try:
                    with json_file.open(
                        "r",
                        encoding="utf-8-sig",
                    ) as handle:
                        data = json.load(handle)
                except (
                    OSError,
                    UnicodeError,
                    json.JSONDecodeError,
                ):
                    continue

                is_history_file = any(
                    part.casefold() in history_folder_names
                    for part in json_file.parts
                )

                if is_history_file:
                    self._collect_string_references(
                        data,
                        history_references,
                    )
                    continue

                self._collect_partitioned_references(
                    data,
                    active_references,
                    history_references,
                )

        return active_references, history_references

    @staticmethod
    def _collect_partitioned_references(
        value,
        active_destination: set[str],
        history_destination: set[str],
        in_history: bool = False,
    ) -> None:
        if isinstance(value, str):
            destination = (
                history_destination
                if in_history
                else active_destination
            )
            ProjectCleanupDialog._collect_string_references(
                value,
                destination,
            )
            return

        if isinstance(value, dict):
            for key, child in value.items():
                normalized_key = str(key).strip().casefold()
                child_in_history = (
                    in_history
                    or normalized_key
                    in {
                        "historique",
                        "history",
                        "versions",
                        "archives",
                    }
                )
                ProjectCleanupDialog._collect_partitioned_references(
                    child,
                    active_destination,
                    history_destination,
                    child_in_history,
                )
            return

        if isinstance(value, list):
            for child in value:
                ProjectCleanupDialog._collect_partitioned_references(
                    child,
                    active_destination,
                    history_destination,
                    in_history,
                )

    @staticmethod
    def _collect_string_references(
        value,
        destination: set[str],
    ) -> None:
        if isinstance(value, str):
            normalized = value.strip().replace(
                "\\",
                "/",
            ).casefold()

            if normalized:
                destination.add(normalized)

            return

        if isinstance(value, dict):
            for child in value.values():
                ProjectCleanupDialog._collect_string_references(
                    child,
                    destination,
                )

            return

        if isinstance(value, list):
            for child in value:
                ProjectCleanupDialog._collect_string_references(
                    child,
                    destination,
                )

    def _find_unused_visual_references(
        self,
        root: Path,
    ) -> tuple[list[dict], int]:
        references = getattr(
            self.project,
            "visual_references",
            [],
        )

        if not isinstance(references, list):
            return [], 0

        used_identifiers = self._used_visual_reference_ids(root)
        unused: list[dict] = []
        total_size = 0

        for summary in references:
            if not isinstance(summary, dict):
                continue

            identifier = str(
                summary.get("identifiant", "")
            ).strip()

            if not identifier or identifier in used_identifiers:
                continue

            unused.append(dict(summary))

            relative_path = str(
                summary.get("fichier", "")
            ).strip()

            if not relative_path:
                continue

            file_path = root / relative_path

            try:
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            except OSError:
                pass

        return unused, total_size

    @staticmethod
    def _used_visual_reference_ids(root: Path) -> set[str]:
        used: set[str] = set()
        search_roots = (
            root / "documents",
            root / "modeles",
            root / "contenus",
            root / "productions",
        )

        for search_root in search_roots:
            if not search_root.exists():
                continue

            try:
                files = search_root.rglob("*.json")
            except OSError:
                continue

            for json_file in files:
                try:
                    with json_file.open(
                        "r",
                        encoding="utf-8-sig",
                    ) as handle:
                        data = json.load(handle)
                except (OSError, UnicodeError, json.JSONDecodeError):
                    continue

                ProjectCleanupDialog._collect_visual_reference_ids(
                    data,
                    used,
                )

        return used

    @staticmethod
    def _collect_visual_reference_ids(
        value,
        destination: set[str],
        parent_key: str = "",
    ) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized_key = str(key)

                if normalized_key == "visuel_temoin_id":
                    identifier = str(child).strip()

                    if identifier:
                        destination.add(identifier)

                    continue

                if normalized_key == "visuels_temoins_ids":
                    if isinstance(child, list):
                        for item in child:
                            identifier = str(item).strip()

                            if identifier:
                                destination.add(identifier)

                    continue

                if (
                    normalized_key == "reference_id"
                    and parent_key == "visuel_temoin_guide"
                ):
                    identifier = str(child).strip()

                    if identifier:
                        destination.add(identifier)

                    continue

                ProjectCleanupDialog._collect_visual_reference_ids(
                    child,
                    destination,
                    normalized_key,
                )

            return

        if isinstance(value, list):
            for child in value:
                ProjectCleanupDialog._collect_visual_reference_ids(
                    child,
                    destination,
                    parent_key,
                )

    @staticmethod
    def _folder_stats(folder: Path) -> tuple[int, int]:
        if not folder.exists():
            return 0, 0

        file_count = 0
        total_size = 0

        try:
            for item in folder.rglob("*"):
                if not item.is_file():
                    continue

                file_count += 1

                try:
                    total_size += item.stat().st_size
                except OSError:
                    pass
        except OSError:
            return file_count, total_size

        return file_count, total_size

    @staticmethod
    def _format_size(size: int) -> str:
        value = float(max(0, size))
        units = ("o", "Ko", "Mo", "Go", "To")

        for unit in units:
            if value < 1024.0 or unit == units[-1]:
                if unit == "o":
                    return f"{int(value)} {unit}"

                return f"{value:.1f} {unit}".replace(".", ",")

            value /= 1024.0

        return f"{int(size)} o"

    def _project_root(self) -> Path | None:
        root = getattr(self.project, "root", None)

        if root is None:
            return None

        try:
            return Path(root)
        except TypeError:
            return None

    # ==========================================================
    # Fenêtre
    # ==========================================================

    def _center_window(self) -> None:
        self.update_idletasks()

        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(
            0,
            (parent.winfo_width() - self.winfo_width()) // 2,
        )
        y = parent.winfo_y() + max(
            0,
            (parent.winfo_height() - self.winfo_height()) // 2,
        )

        self.geometry(f"+{x}+{y}")

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        try:
            self.destroy()
        finally:
            if self.on_close is not None:
                self.on_close()