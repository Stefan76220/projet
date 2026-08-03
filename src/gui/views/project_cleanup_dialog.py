from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Callable
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.theme.interface_assets import InterfaceAssets


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
        self.transient(parent.winfo_toplevel())
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
            padx=20,
            pady=16,
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
            pady=(0, 6),
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
        if path.is_dir():
            _, total_size = ProjectCleanupDialog._folder_stats(path)
            return total_size

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
        delete_callback: Callable[[Path], None],
    ) -> None:
        super().__init__(parent)

        self.project_root = project_root
        self.trash_root = project_root / "corbeille"
        self.restore_callback = restore_callback
        self.delete_callback = delete_callback

        self.title("Contenu de la corbeille")
        self.geometry("900x640")
        self.minsize(780, 520)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
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
                padx=(0, 8),
            )

            ctk.CTkButton(
                row,
                text="Supprimer ce lot",
                width=150,
                height=34,
                fg_color="#B42318",
                hover_color="#8F1C14",
                text_color="#FFFFFF",
                command=lambda selected=batch: self._delete(selected),
            ).grid(
                row=0,
                column=3,
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

    def _delete(self, batch: Path) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass

        try:
            self.delete_callback(batch)
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

        if name.startswith("modeles_"):
            return "Modèles"

        if name.startswith("fiches_contenu_"):
            return "Fiches de contenu"

        if name.startswith("collections_contenu_"):
            return "Collections de contenu"

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


class ProjectCleanupDialog(ctk.CTkFrame):
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
        self._unused_models: list[Path] = []
        self._unused_models_size = 0
        self._latest_trash_models: Path | None = None
        self._unused_content_sheets: list[Path] = []
        self._unused_content_sheets_size = 0
        self._unused_content_collections: list[Path] = []
        self._unused_content_collections_size = 0
        self._latest_trash_content_sheets: Path | None = None
        self._latest_trash_content_collections: Path | None = None

        self.configure(
            fg_color="#F8FAF7",
            corner_radius=0,
        )
        self.pack(
            fill="both",
            expand=True,
        )

        self._build()
        self.analyze()

    # ==========================================================
    # Construction
    # ==========================================================

    def _build(self) -> None:
        paper = "#F7FAF5"
        card = "#FEFFFE"
        pearl = "#D4E0E5"
        ink = "#21384A"
        blue = "#356F9F"
        celadon = "#91D1B5"
        sky = "#8EC5EA"
        lilac = "#B7A6E0"
        coral = "#F08B72"
        turquoise = "#65C3C8"
        sun = "#F2D66B"
        panel_shadow = "#D4DEDC"
        cool_shadow = "#CFD9E1"

        def load_asset(
            family: str,
            filename: str,
            max_size: tuple[int, int],
            *,
            crop_transparency: bool = True,
            separator_crop: bool = False,
        ) -> ctk.CTkImage | None:
            path = InterfaceAssets.path(
                family,
                filename,
            )

            if not path.is_file():
                return None

            try:
                with Image.open(path) as source_image:
                    image = source_image.convert("RGBA")

                if crop_transparency:
                    if separator_crop:
                        width, height = image.size
                        bounds = (
                            round(width * 0.04),
                            round(height * 0.38),
                            round(width * 0.96),
                            round(height * 0.62),
                        )
                    else:
                        bounds = image.getbbox()

                    if bounds is not None:
                        image = image.crop(bounds)

                width, height = image.size
                max_width, max_height = max_size

                scale = min(
                    max_width / max(width, 1),
                    max_height / max(height, 1),
                )
                display_size = (
                    max(1, round(width * scale)),
                    max(1, round(height * scale)),
                )

                return ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=display_size,
                )
            except (OSError, ValueError):
                return None

        self._paper_image = load_asset(
            "textures",
            "papier_clair.png",
            (1600, 1000),
            crop_transparency=False,
        )
        self._corner_image = load_asset(
            "coins",
            "angle_livre.png",
            (96, 56),
        )
        self._separator_image = load_asset(
            "separateurs",
            "separateur_livre.png",
            (340, 30),
            separator_crop=True,
        )

        if self._paper_image is not None:
            background = ctk.CTkLabel(
                self,
                text="",
                image=self._paper_image,
                fg_color=paper,
            )
            background.place(
                x=0,
                y=0,
                relwidth=1,
                relheight=1,
            )
            background.lower()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(
            self,
            height=48,
            fg_color="#FCFEFC",
            corner_radius=0,
            border_width=1,
            border_color="#E3E9E7",
        )
        toolbar.grid(
            row=0,
            column=0,
            sticky="ew",
        )
        toolbar.grid_propagate(False)
        toolbar.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            toolbar,
            text="←  Centre du projet",
            width=160,
            height=32,
            corner_radius=7,
            fg_color="#EEF3F6",
            hover_color="#DFE8EE",
            text_color=ink,
            font=Fonts.NORMAL,
            command=self.close,
        ).grid(
            row=0,
            column=0,
            padx=(18, 10),
            pady=8,
        )

        ctk.CTkLabel(
            toolbar,
            text="Outils du projet  /  Nettoyage de la base",
            font=Fonts.SMALL,
            height=16,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=0,
            column=1,
            sticky="ew",
        )

        ctk.CTkButton(
            toolbar,
            text="Actualiser",
            width=100,
            height=32,
            corner_radius=7,
            fg_color="#EDF4FA",
            hover_color="#DDEBF5",
            text_color=blue,
            command=self.analyze,
        ).grid(
            row=0,
            column=2,
            padx=(10, 18),
            pady=8,
        )

        page = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        page.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(8, 5),
        )
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(3, weight=1, minsize=205)

        header_shadow = ctk.CTkFrame(
            page,
            height=76,
            fg_color=panel_shadow,
            corner_radius=14,
        )
        header_shadow.grid(
            row=0,
            column=0,
            sticky="ew",
        )
        header_shadow.grid_propagate(False)

        header = ctk.CTkFrame(
            header_shadow,
            fg_color="#FFFFFF",
            corner_radius=13,
            border_width=1,
            border_color="#C9D6D9",
        )
        header.pack(
            fill="both",
            expand=True,
            padx=(0, 2),
            pady=(0, 3),
        )
        header.grid_columnconfigure(1, weight=1)
        header.grid_rowconfigure(1, weight=1)

        ctk.CTkFrame(
            header,
            height=2,
            fg_color="#FFFFFF",
            corner_radius=1,
        ).place(
            x=18,
            y=3,
            relwidth=0.97,
        )

        top_rule = ctk.CTkFrame(
            header,
            height=1,
            fg_color=ink,
            corner_radius=0,
        )
        top_rule.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=(20, 16),
            pady=(6, 0),
        )

        corner_holder = ctk.CTkFrame(
            header,
            width=108,
            height=56,
            fg_color="transparent",
        )
        corner_holder.grid(
            row=1,
            column=0,
            sticky="nw",
            padx=(11, 5),
            pady=(0, 2),
        )
        corner_holder.grid_propagate(False)

        if self._corner_image is not None:
            ctk.CTkLabel(
                corner_holder,
                text="",
                image=self._corner_image,
                fg_color="transparent",
            ).pack(
                anchor="nw",
            )
        else:
            ctk.CTkFrame(
                corner_holder,
                width=1,
                height=72,
                fg_color=ink,
                corner_radius=0,
            ).pack(
                side="left",
                padx=(10, 0),
                pady=(4, 0),
            )

        title_guide = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )
        title_guide.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(0, 16),
            pady=(0, 2),
        )
        title_guide.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(
            title_guide,
            width=1,
            fg_color=ink,
            corner_radius=0,
        ).grid(
            row=0,
            column=0,
            rowspan=3,
            sticky="ns",
            padx=(0, 10),
        )

        ctk.CTkFrame(
            title_guide,
            width=8,
            height=8,
            fg_color=celadon,
            corner_radius=2,
        ).grid(
            row=0,
            column=0,
            sticky="n",
            padx=(0, 10),
            pady=(1, 0),
        )

        project_name = str(
            getattr(self.project, "name", "")
            or "Projet sans nom"
        )
        root = self._project_root()

        ctk.CTkLabel(
            title_guide,
            text="Nettoyage de la base",
            font=Fonts.H1,
            height=24,
            text_color=ink,
            anchor="w",
        ).grid(
            row=0,
            column=1,
            sticky="ew",
        )

        ctk.CTkLabel(
            title_guide,
            text=f"Projet analysé : {project_name}",
            font=Fonts.NORMAL,
            height=18,
            text_color=blue,
            anchor="w",
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            pady=0,
        )

        ctk.CTkLabel(
            title_guide,
            text=(
                str(root)
                if root is not None
                else "Dossier indisponible"
            ),
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=2,
            column=1,
            sticky="ew",
            pady=0,
        )

        separator_holder = ctk.CTkFrame(
            page,
            height=32,
            fg_color="transparent",
        )
        separator_holder.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 3),
        )
        separator_holder.grid_propagate(False)

        if self._separator_image is not None:
            ctk.CTkLabel(
                separator_holder,
                text="",
                image=self._separator_image,
                fg_color="transparent",
            ).pack()
        else:
            ctk.CTkFrame(
                separator_holder,
                height=1,
                fg_color=pearl,
            ).pack(
                fill="x",
                padx=360,
                pady=10,
            )

        self.total_var = tk.StringVar(
            value="Analyse en cours…"
        )
        self.cache_recoverable_var = tk.StringVar(
            value="—"
        )
        self.unused_visuals_var = tk.StringVar(
            value="Analyse en cours…"
        )
        self.unused_graphics_var = tk.StringVar(
            value="Analyse en cours…"
        )
        self.history_only_graphics_var = tk.StringVar(
            value="Analyse en cours…"
        )
        self.unused_models_var = tk.StringVar(
            value="Analyse en cours…"
        )
        self.unused_content_sheets_var = tk.StringVar(
            value="Analyse en cours…"
        )
        self.unused_content_collections_var = tk.StringVar(
            value="Analyse en cours…"
        )

        overview = ctk.CTkFrame(
            page,
            fg_color="transparent",
        )
        overview.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 8),
        )
        overview.grid_columnconfigure(0, weight=1)
        overview.grid_columnconfigure(1, weight=1)

        def create_card_title(
            parent,
            text: str,
            accent: str,
            background: str,
        ) -> None:
            title_shadow = ctk.CTkFrame(
                parent,
                fg_color="#DCE5E3",
                corner_radius=9,
            )
            title_shadow.grid(
                row=0,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=8,
                pady=(6, 4),
            )

            title = ctk.CTkFrame(
                title_shadow,
                fg_color=background,
                corner_radius=8,
                border_width=1,
                border_color="#FFFFFF",
            )
            title.pack(
                fill="both",
                expand=True,
                padx=(0, 1),
                pady=(0, 2),
            )

            ctk.CTkFrame(
                title,
                width=6,
                height=20,
                fg_color=accent,
                corner_radius=3,
            ).pack(
                side="left",
                padx=(8, 7),
                pady=4,
            )

            ctk.CTkLabel(
                title,
                text=text,
                font=Fonts.NORMAL,
                text_color=ink,
                anchor="w",
            ).pack(
                side="left",
                pady=4,
            )

        occupation_shadow = ctk.CTkFrame(
            overview,
            fg_color=panel_shadow,
            corner_radius=13,
        )
        occupation_shadow.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 6),
        )

        occupation = ctk.CTkFrame(
            occupation_shadow,
            fg_color="#FCFFFD",
            corner_radius=12,
            border_width=1,
            border_color="#BDD8CC",
        )
        occupation.pack(
            fill="both",
            expand=True,
            padx=(0, 2),
            pady=(0, 3),
        )
        occupation.grid_columnconfigure(0, weight=1)
        occupation.grid_columnconfigure(1, weight=1)

        create_card_title(
            occupation,
            "Occupation du projet",
            celadon,
            "#DFF3E9",
        )

        for index, (label, folder_name) in enumerate(
            self.CATEGORY_FOLDERS
        ):
            row_index = 1 + index // 2
            column_index = index % 2

            item = ctk.CTkFrame(
                occupation,
                fg_color=(
                    "#EDF8F2"
                    if row_index % 2 == 1
                    else "#F8FCFA"
                ),
                corner_radius=6,
            )
            item.grid(
                row=row_index,
                column=column_index,
                sticky="ew",
                padx=(
                    (8, 4)
                    if column_index == 0
                    else (4, 8)
                ),
                pady=2,
            )
            item.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                item,
                text=label,
                font=Fonts.SMALL,
                text_color=ink,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=(8, 4),
                pady=4,
            )

            count_label = ctk.CTkLabel(
                item,
                text="—",
                width=34,
                font=Fonts.SMALL,
                text_color=Colors.TEXT_LIGHT,
                anchor="e",
            )
            count_label.grid(
                row=0,
                column=1,
                padx=(4, 2),
                pady=4,
            )

            size_label = ctk.CTkLabel(
                item,
                text="—",
                width=66,
                font=Fonts.SMALL,
                text_color=Colors.TEXT_LIGHT,
                anchor="e",
            )
            size_label.grid(
                row=0,
                column=2,
                padx=(2, 8),
                pady=4,
            )

            self._rows[folder_name] = (
                count_label,
                size_label,
            )

        summary_shadow = ctk.CTkFrame(
            overview,
            fg_color=cool_shadow,
            corner_radius=13,
        )
        summary_shadow.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 0),
        )

        summary = ctk.CTkFrame(
            summary_shadow,
            fg_color="#FCFDFF",
            corner_radius=12,
            border_width=1,
            border_color="#BDD2E4",
        )
        summary.pack(
            fill="both",
            expand=True,
            padx=(0, 2),
            pady=(0, 3),
        )
        summary.grid_columnconfigure(0, weight=1)
        summary.grid_columnconfigure(1, weight=1)

        create_card_title(
            summary,
            "Éléments détectés",
            sky,
            "#E2F0FB",
        )

        summary_items = (
            ("Taille totale", self.total_var, blue),
            ("Cache", self.cache_recoverable_var, blue),
            ("Visuels", self.unused_visuals_var, blue),
            ("Graphiques", self.unused_graphics_var, blue),
            (
                "Historique",
                self.history_only_graphics_var,
                "#A36342",
            ),
            ("Modèles", self.unused_models_var, blue),
            ("Fiches", self.unused_content_sheets_var, blue),
            (
                "Collections",
                self.unused_content_collections_var,
                blue,
            ),
        )
        accent_colors = (
            sky,
            turquoise,
            lilac,
            celadon,
        )

        for index, (label, variable, text_color) in enumerate(
            summary_items
        ):
            row_index = 1 + index // 2
            column_index = index % 2

            item = ctk.CTkFrame(
                summary,
                fg_color=(
                    "#EDF5FC"
                    if row_index % 2 == 1
                    else "#F8FBFE"
                ),
                corner_radius=6,
            )
            item.grid(
                row=row_index,
                column=column_index,
                sticky="ew",
                padx=(
                    (8, 4)
                    if column_index == 0
                    else (4, 8)
                ),
                pady=2,
            )
            item.grid_columnconfigure(1, weight=1)

            ctk.CTkFrame(
                item,
                width=4,
                height=14,
                fg_color=accent_colors[index % 4],
                corner_radius=2,
            ).grid(
                row=0,
                column=0,
                padx=(7, 5),
                pady=4,
            )

            ctk.CTkLabel(
                item,
                text=label,
                font=Fonts.SMALL,
                text_color=ink,
                anchor="w",
            ).grid(
                row=0,
                column=1,
                sticky="ew",
                padx=(0, 4),
                pady=4,
            )

            ctk.CTkLabel(
                item,
                textvariable=variable,
                width=138,
                font=Fonts.SMALL,
                text_color=text_color,
                anchor="e",
            ).grid(
                row=0,
                column=2,
                padx=(4, 8),
                pady=4,
            )

        actions_shadow = ctk.CTkFrame(
            page,
            fg_color=cool_shadow,
            corner_radius=15,
        )
        actions_shadow.grid(
            row=3,
            column=0,
            sticky="nsew",
            pady=(2, 3),
        )

        actions = ctk.CTkFrame(
            actions_shadow,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color="#C4D1D9",
        )
        actions.pack(
            fill="both",
            expand=True,
            padx=(0, 2),
            pady=(0, 3),
        )
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_rowconfigure(1, weight=1)

        tab_strip = ctk.CTkFrame(
            actions,
            height=44,
            fg_color=paper,
            corner_radius=0,
        )
        tab_strip.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(5, 0),
        )
        tab_strip.grid_propagate(False)
        tab_strip.grid_columnconfigure(3, weight=1)

        content_host = ctk.CTkFrame(
            actions,
            fg_color="#FFFFFF",
            corner_radius=11,
            border_width=1,
            border_color="#C4D1D9",
        )
        content_host.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 10),
        )

        cleanup_tab = ctk.CTkFrame(
            content_host,
            fg_color="#FFFFFF",
            corner_radius=10,
        )
        libraries_tab = ctk.CTkFrame(
            content_host,
            fg_color="#FFFFFF",
            corner_radius=10,
        )
        trash_tab = ctk.CTkFrame(
            content_host,
            fg_color="#FFFFFF",
            corner_radius=10,
        )

        for tab_page in (
            cleanup_tab,
            libraries_tab,
            trash_tab,
        ):
            tab_page.place(
                x=0,
                y=0,
                relwidth=1,
                relheight=1,
            )

        tab_specs = (
            ("Nettoyage courant", cleanup_tab, celadon),
            ("Bibliothèques", libraries_tab, lilac),
            ("Corbeille", trash_tab, coral),
        )
        tab_canvases: dict[str, tk.Canvas] = {}

        def draw_folder_tab(
            canvas: tk.Canvas,
            label: str,
            accent: str,
            active: bool,
        ) -> None:
            canvas.delete("all")

            width = 184
            height = 42
            top = 1 if active else 7
            fill = "#FFFFFF" if active else "#E6EDF1"
            outline = "#9FB0BA" if active else "#C3CDD3"
            text_color = ink if active else "#566A78"

            points = (
                2, height - 1,
                2, top + 10,
                13, top + 10,
                20, top + 2,
                width - 12, top + 2,
                width - 2, top + 11,
                width - 2, height - 1,
            )

            canvas.create_polygon(
                points,
                fill=fill,
                outline=outline,
                width=1,
                smooth=False,
            )
            canvas.create_line(
                20,
                top + 3,
                width - 18,
                top + 3,
                fill=accent,
                width=4,
            )
            canvas.create_rectangle(
                13,
                top + 13,
                20,
                top + 20,
                fill=accent,
                outline="",
            )
            canvas.create_text(
                width // 2 + 4,
                top + 22,
                text=label,
                fill=text_color,
                font=(
                    "Segoe UI Semibold"
                    if active
                    else "Segoe UI",
                    10,
                ),
            )

        def show_tab(tab_name: str) -> None:
            selected_page = next(
                page_widget
                for name, page_widget, _ in tab_specs
                if name == tab_name
            )
            selected_page.tkraise()

            for name, _, accent in tab_specs:
                draw_folder_tab(
                    tab_canvases[name],
                    name,
                    accent,
                    name == tab_name,
                )

        for column, (name, _, accent) in enumerate(tab_specs):
            canvas = tk.Canvas(
                tab_strip,
                width=184,
                height=42,
                bg=paper,
                highlightthickness=0,
                borderwidth=0,
                cursor="hand2",
            )
            canvas.grid(
                row=0,
                column=column,
                sticky="s",
                padx=(0, 4),
            )
            canvas.bind(
                "<Button-1>",
                lambda _event, tab_name=name: show_tab(tab_name),
            )
            tab_canvases[name] = canvas

        cleanup_scroll = ctk.CTkScrollableFrame(
            cleanup_tab,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#BFCBD2",
            scrollbar_button_hover_color="#9FADB7",
        )
        cleanup_scroll.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=7,
        )

        libraries_scroll = ctk.CTkScrollableFrame(
            libraries_tab,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#BFCBD2",
            scrollbar_button_hover_color="#9FADB7",
        )
        libraries_scroll.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=7,
        )

        trash_scroll = ctk.CTkScrollableFrame(
            trash_tab,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#BFCBD2",
            scrollbar_button_hover_color="#9FADB7",
        )
        trash_scroll.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=7,
        )

        show_tab("Nettoyage courant")

        icon_font = (
            "Segoe MDL2 Assets",
            14,
        )
        icon_detail = "\uE946"
        icon_trash = "\uE74D"
        icon_restore = "\uE7A7"
        icon_view = "\uE890"

        def configure_action_table(parent) -> None:
            parent.grid_columnconfigure(0, weight=1)
            parent.grid_columnconfigure(1, minsize=185)
            parent.grid_columnconfigure(2, minsize=58)
            parent.grid_columnconfigure(3, minsize=70)
            parent.grid_columnconfigure(4, minsize=70)

            headers = (
                ("Élément", 0, "w"),
                ("État", 1, "e"),
                ("Détail", 2, "center"),
                ("Corbeille", 3, "center"),
                ("Restaurer", 4, "center"),
            )

            for label, column, anchor in headers:
                ctk.CTkLabel(
                    parent,
                    text=label,
                    font=Fonts.SMALL,
                    text_color=Colors.TEXT_LIGHT,
                    anchor=anchor,
                ).grid(
                    row=0,
                    column=column,
                    sticky="ew",
                    padx=6,
                    pady=(5, 3),
                )

        def make_icon_button(
            parent,
            *,
            glyph: str,
            command,
            kind: str,
        ):
            if kind == "detail":
                fg_color = "#EDF4FA"
                hover_color = "#DDEBF5"
                text_color = blue
            elif kind == "trash":
                fg_color = "#FFF1ED"
                hover_color = "#FBE1D8"
                text_color = "#B05D48"
            else:
                fg_color = "#EDF7F2"
                hover_color = "#DCEDE4"
                text_color = "#3E775C"

            border_color = {
                "detail": "#B9D5E8",
                "trash": "#F0C8BB",
                "restore": "#BBDCCB",
            }[kind]

            return ctk.CTkButton(
                parent,
                text=glyph,
                width=32,
                height=29,
                corner_radius=7,
                fg_color=fg_color,
                hover_color=hover_color,
                border_width=1,
                border_color=border_color,
                text_color=text_color,
                text_color_disabled="#A9B0B7",
                font=icon_font,
                command=command,
                state="disabled",
            )

        def add_action_row(
            parent,
            *,
            row: int,
            label: str,
            state_variable,
            detail_attribute: str,
            detail_command,
            move_attribute: str,
            move_command,
            restore_attribute: str,
            restore_command,
        ) -> None:
            row_frame = ctk.CTkFrame(
                parent,
                fg_color=(
                    "#EFF6FA"
                    if row % 2 == 1
                    else "#F8FCFA"
                ),
                corner_radius=7,
                border_width=1,
                border_color=(
                    "#D6E4EC"
                    if row % 2 == 1
                    else "#DDEAE3"
                ),
            )
            row_frame.grid(
                row=row,
                column=0,
                columnspan=5,
                sticky="ew",
                padx=3,
                pady=2,
            )
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, minsize=185)
            row_frame.grid_columnconfigure(2, minsize=58)
            row_frame.grid_columnconfigure(3, minsize=70)
            row_frame.grid_columnconfigure(4, minsize=70)

            ctk.CTkLabel(
                row_frame,
                text=label,
                font=Fonts.NORMAL,
                text_color=ink,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=(10, 6),
                pady=4,
            )

            ctk.CTkLabel(
                row_frame,
                textvariable=state_variable,
                font=Fonts.SMALL,
                text_color=Colors.TEXT_LIGHT,
                anchor="e",
            ).grid(
                row=0,
                column=1,
                sticky="ew",
                padx=6,
                pady=4,
            )

            detail_button = make_icon_button(
                row_frame,
                glyph=icon_detail,
                command=detail_command,
                kind="detail",
            )
            detail_button.grid(
                row=0,
                column=2,
                padx=6,
                pady=3,
            )
            setattr(
                self,
                detail_attribute,
                detail_button,
            )

            move_button = make_icon_button(
                row_frame,
                glyph=icon_trash,
                command=move_command,
                kind="trash",
            )
            move_button.grid(
                row=0,
                column=3,
                padx=6,
                pady=3,
            )
            setattr(
                self,
                move_attribute,
                move_button,
            )

            restore_button = make_icon_button(
                row_frame,
                glyph=icon_restore,
                command=restore_command,
                kind="restore",
            )
            restore_button.grid(
                row=0,
                column=4,
                padx=6,
                pady=3,
            )
            setattr(
                self,
                restore_attribute,
                restore_button,
            )

        configure_action_table(cleanup_scroll)

        add_action_row(
            cleanup_scroll,
            row=1,
            label="Cache temporaire",
            state_variable=self.cache_recoverable_var,
            detail_attribute="show_cache_details_button",
            detail_command=self.show_cache_details,
            move_attribute="move_cache_button",
            move_command=self.move_cache_to_trash,
            restore_attribute="restore_cache_button",
            restore_command=self.restore_latest_cache,
        )

        add_action_row(
            cleanup_scroll,
            row=2,
            label="Visuels témoins inutilisés",
            state_variable=self.unused_visuals_var,
            detail_attribute="show_visuals_details_button",
            detail_command=self.show_unused_visuals_details,
            move_attribute="move_unused_visuals_button",
            move_command=self.move_unused_visuals_to_trash,
            restore_attribute="restore_visuals_button",
            restore_command=self.restore_latest_visuals,
        )

        add_action_row(
            cleanup_scroll,
            row=3,
            label="Ressources graphiques inutilisées",
            state_variable=self.unused_graphics_var,
            detail_attribute="show_graphics_details_button",
            detail_command=self.show_unused_graphics_details,
            move_attribute="move_unused_graphics_button",
            move_command=self.move_unused_graphics_to_trash,
            restore_attribute="restore_graphics_button",
            restore_command=self.restore_latest_graphics,
        )

        configure_action_table(libraries_scroll)

        add_action_row(
            libraries_scroll,
            row=1,
            label="Ressources liées uniquement à l’historique",
            state_variable=self.history_only_graphics_var,
            detail_attribute="show_history_graphics_details_button",
            detail_command=self.show_history_only_graphics_details,
            move_attribute="move_history_graphics_button",
            move_command=self.move_history_only_graphics_to_trash,
            restore_attribute="restore_history_graphics_button",
            restore_command=self.restore_latest_history_graphics,
        )

        add_action_row(
            libraries_scroll,
            row=2,
            label="Modèles inutilisés",
            state_variable=self.unused_models_var,
            detail_attribute="show_unused_models_details_button",
            detail_command=self.show_unused_models_details,
            move_attribute="move_unused_models_button",
            move_command=self.move_unused_models_to_trash,
            restore_attribute="restore_models_button",
            restore_command=self.restore_latest_models,
        )

        add_action_row(
            libraries_scroll,
            row=3,
            label="Fiches de contenu inutilisées",
            state_variable=self.unused_content_sheets_var,
            detail_attribute="show_unused_content_sheets_button",
            detail_command=self.show_unused_content_sheets_details,
            move_attribute="move_unused_content_sheets_button",
            move_command=self.move_unused_content_sheets_to_trash,
            restore_attribute="restore_content_sheets_button",
            restore_command=self.restore_latest_content_sheets,
        )

        add_action_row(
            libraries_scroll,
            row=4,
            label="Collections inutilisées",
            state_variable=self.unused_content_collections_var,
            detail_attribute="show_unused_content_collections_button",
            detail_command=self.show_unused_content_collections_details,
            move_attribute="move_unused_content_collections_button",
            move_command=self.move_unused_content_collections_to_trash,
            restore_attribute="restore_content_collections_button",
            restore_command=self.restore_latest_content_collections,
        )

        trash_scroll.grid_columnconfigure(0, weight=1)
        trash_scroll.grid_columnconfigure(1, minsize=185)
        trash_scroll.grid_columnconfigure(2, minsize=70)

        for label, column, anchor in (
            ("Action", 0, "w"),
            ("État", 1, "e"),
            ("Exécuter", 2, "center"),
        ):
            ctk.CTkLabel(
                trash_scroll,
                text=label,
                font=Fonts.SMALL,
                text_color=Colors.TEXT_LIGHT,
                anchor=anchor,
            ).grid(
                row=0,
                column=column,
                sticky="ew",
                padx=6,
                pady=(5, 3),
            )

        trash_view_row = ctk.CTkFrame(
            trash_scroll,
            fg_color="#EFF6FA",
            corner_radius=7,
            border_width=1,
            border_color="#D6E4EC",
        )
        trash_view_row.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=3,
            pady=2,
        )
        trash_view_row.grid_columnconfigure(0, weight=1)
        trash_view_row.grid_columnconfigure(1, minsize=185)
        trash_view_row.grid_columnconfigure(2, minsize=70)

        ctk.CTkLabel(
            trash_view_row,
            text="Consulter les lots de la corbeille",
            font=Fonts.NORMAL,
            text_color=ink,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=5,
        )

        ctk.CTkLabel(
            trash_view_row,
            text="Restauration lot par lot",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="e",
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=6,
            pady=5,
        )

        self.view_trash_button = ctk.CTkButton(
            trash_view_row,
            text=icon_view,
            width=31,
            height=28,
            corner_radius=6,
            fg_color="#EDF4FA",
            hover_color="#DDEBF5",
            text_color=blue,
            text_color_disabled="#A9B0B7",
            font=icon_font,
            command=self.show_trash_contents,
            state="disabled",
        )
        self.view_trash_button.grid(
            row=0,
            column=2,
            padx=6,
            pady=3,
        )

        trash_empty_row = ctk.CTkFrame(
            trash_scroll,
            fg_color="#FFF7F4",
            corner_radius=7,
            border_width=1,
            border_color="#F0D4CB",
        )
        trash_empty_row.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=3,
            pady=2,
        )
        trash_empty_row.grid_columnconfigure(0, weight=1)
        trash_empty_row.grid_columnconfigure(1, minsize=185)
        trash_empty_row.grid_columnconfigure(2, minsize=70)

        ctk.CTkLabel(
            trash_empty_row,
            text="Vider définitivement la corbeille",
            font=Fonts.NORMAL,
            text_color=ink,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=5,
        )

        ctk.CTkLabel(
            trash_empty_row,
            text="Action irréversible",
            font=Fonts.SMALL,
            text_color="#A44A3A",
            anchor="e",
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=6,
            pady=5,
        )

        self.empty_trash_button = ctk.CTkButton(
            trash_empty_row,
            text=icon_trash,
            width=31,
            height=28,
            corner_radius=6,
            fg_color="#FFF1ED",
            hover_color="#FBE1D8",
            text_color="#B05D48",
            text_color_disabled="#A9B0B7",
            font=icon_font,
            command=self.empty_trash,
            state="disabled",
        )
        self.empty_trash_button.grid(
            row=0,
            column=2,
            padx=6,
            pady=3,
        )

        footer = ctk.CTkFrame(
            self,
            height=36,
            fg_color="#FCFEFC",
            corner_radius=0,
            border_width=1,
            border_color="#DEE7E3",
        )
        footer.grid(
            row=2,
            column=0,
            sticky="ew",
        )
        footer.grid_propagate(False)
        footer.grid_columnconfigure(1, weight=1)

        self.status_var = tk.StringVar(
            value=(
                "Analyse du projet en cours. "
                "Les suppressions passent d’abord "
                "par la corbeille interne."
            )
        )

        ctk.CTkFrame(
            footer,
            width=5,
            height=20,
            fg_color=lilac,
            corner_radius=3,
        ).grid(
            row=0,
            column=0,
            padx=(18, 8),
            pady=8,
        )

        ctk.CTkLabel(
            footer,
            textvariable=self.status_var,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=0,
            column=1,
            sticky="ew",
        )

        ctk.CTkLabel(
            footer,
            text="PageMaître · nettoyage sécurisé",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
        ).grid(
            row=0,
            column=2,
            padx=(10, 18),
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

        (
            self._unused_models,
            self._unused_models_size,
        ) = self._find_unused_models(root)
        self.unused_models_var.set(
            f"{len(self._unused_models)} modèle(s) — "
            f"{self._format_size(self._unused_models_size)}"
        )
        models_state = (
            "normal"
            if self._unused_models
            else "disabled"
        )
        self.show_unused_models_details_button.configure(
            state=models_state
        )
        self.move_unused_models_button.configure(
            state=models_state
        )

        self._latest_trash_models = self._find_latest_trash_models(
            root
        )
        self.restore_models_button.configure(
            state=(
                "normal"
                if self._latest_trash_models is not None
                else "disabled"
            )
        )

        (
            self._unused_content_sheets,
            self._unused_content_sheets_size,
        ) = self._find_unused_content_sheets(root)
        self.unused_content_sheets_var.set(
            f"{len(self._unused_content_sheets)} fiche(s) — "
            f"{self._format_size(self._unused_content_sheets_size)}"
        )
        sheets_state = (
            "normal"
            if self._unused_content_sheets
            else "disabled"
        )
        self.show_unused_content_sheets_button.configure(
            state=sheets_state
        )
        self.move_unused_content_sheets_button.configure(
            state=sheets_state
        )

        self._latest_trash_content_sheets = (
            self._find_latest_trash_content_sheets(root)
        )
        self.restore_content_sheets_button.configure(
            state=(
                "normal"
                if self._latest_trash_content_sheets is not None
                else "disabled"
            )
        )

        (
            self._unused_content_collections,
            self._unused_content_collections_size,
        ) = self._find_unused_content_collections(root)
        self.unused_content_collections_var.set(
            f"{len(self._unused_content_collections)} collection(s) — "
            f"{self._format_size(self._unused_content_collections_size)}"
        )
        collections_state = (
            "normal"
            if self._unused_content_collections
            else "disabled"
        )
        self.show_unused_content_collections_button.configure(
            state=collections_state
        )
        self.move_unused_content_collections_button.configure(
            state=collections_state
        )

        self._latest_trash_content_collections = (
            self._find_latest_trash_content_collections(root)
        )
        self.restore_content_collections_button.configure(
            state=(
                "normal"
                if self._latest_trash_content_collections is not None
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
        elif self._unused_models:
            self.status_var.set(
                f"{len(self._unused_models)} modèle(s) ne sont associés "
                "à aucune page, fiche, collection ou production."
            )
        elif self._latest_trash_models is not None:
            self.status_var.set(
                "Le dernier lot de modèles placé dans la corbeille "
                "peut être restauré."
            )
        elif self._unused_content_sheets:
            self.status_var.set(
                f"{len(self._unused_content_sheets)} fiche(s) de contenu "
                "ne sont associées à aucune collection, page ou production."
            )
        elif self._unused_content_collections:
            self.status_var.set(
                f"{len(self._unused_content_collections)} collection(s) "
                "ne sont associées à aucune production."
            )
        elif self._latest_trash_content_sheets is not None:
            self.status_var.set(
                "Le dernier lot de fiches de contenu peut être restauré."
            )
        elif self._latest_trash_content_collections is not None:
            self.status_var.set(
                "Le dernier lot de collections peut être restauré."
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
            delete_callback=self.delete_trash_batch,
        )

    def delete_trash_batch(self, batch: Path) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        trash_root = root / "corbeille"

        try:
            resolved_trash = trash_root.resolve()
            resolved_batch = batch.resolve()
        except OSError:
            resolved_trash = trash_root
            resolved_batch = batch

        if (
            not batch.exists()
            or not batch.is_dir()
            or resolved_batch.parent != resolved_trash
        ):
            messagebox.showerror(
                "Lot indisponible",
                (
                    "Le lot sélectionné n’existe plus ou ne se trouve "
                    "pas directement dans la corbeille du projet."
                ),
                parent=self,
            )
            self.analyze()
            return

        file_count, batch_size = self._folder_stats(batch)
        lot_name = TrashContentsDialog._batch_label(batch)

        first_confirmation = messagebox.askyesno(
            "Suppression définitive du lot",
            (
                f"Lot : {lot_name}\n"
                f"{file_count} fichier(s) — "
                f"{self._format_size(batch_size)}\n\n"
                "Ce lot sera supprimé définitivement et ne pourra plus "
                "être restauré.\n\n"
                "Continuer ?"
            ),
            parent=self,
        )

        if not first_confirmation:
            return

        second_confirmation = messagebox.askyesno(
            "Dernière confirmation",
            (
                "La suppression est irréversible.\n\n"
                f"Supprimer définitivement le lot « {lot_name} » ?"
            ),
            parent=self,
        )

        if not second_confirmation:
            return

        try:
            shutil.rmtree(batch)
        except OSError as exc:
            messagebox.showerror(
                "Suppression impossible",
                (
                    "Le lot n’a pas pu être supprimé correctement.\n\n"
                    f"{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"Le lot « {lot_name} » a été supprimé définitivement."
        )

        messagebox.showinfo(
            "Lot supprimé",
            (
                f"Le lot « {lot_name} » a été supprimé définitivement.\n"
                "Les autres lots de la corbeille sont conservés."
            ),
            parent=self,
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

        if name.startswith("modeles_"):
            self.restore_latest_models(batch)
            return

        if name.startswith("fiches_contenu_"):
            self.restore_latest_content_sheets(batch)
            return

        if name.startswith("collections_contenu_"):
            self.restore_latest_content_collections(batch)
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

    def move_unused_content_sheets_to_trash(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        folders, _ = self._find_unused_content_sheets(root)

        self._move_unused_content_folders_to_trash(
            root=root,
            folders=folders,
            batch_prefix="fiches_contenu",
            manifest_type="fiches_contenu",
            definition_name="fiche.json",
            index_attribute="content_sheets",
            item_label="fiche(s) de contenu",
            confirmation_title="Mettre les fiches à la corbeille",
        )

    def move_unused_content_collections_to_trash(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        folders, _ = self._find_unused_content_collections(root)

        self._move_unused_content_folders_to_trash(
            root=root,
            folders=folders,
            batch_prefix="collections_contenu",
            manifest_type="collections_contenu",
            definition_name="collection.json",
            index_attribute="content_collections",
            item_label="collection(s) de contenu",
            confirmation_title="Mettre les collections à la corbeille",
        )

    def _move_unused_content_folders_to_trash(
        self,
        *,
        root: Path,
        folders: list[Path],
        batch_prefix: str,
        manifest_type: str,
        definition_name: str,
        index_attribute: str,
        item_label: str,
        confirmation_title: str,
    ) -> None:
        if not folders:
            messagebox.showinfo(
                "Aucun contenu inutilisé",
                f"Aucune {item_label} inutilisée n’a été détectée.",
                parent=self,
            )
            self.analyze()
            return

        confirmed = messagebox.askyesno(
            confirmation_title,
            (
                f"{len(folders)} {item_label} ne sont associées à aucun "
                "élément actif du projet.\n\n"
                "Elles seront déplacées dans la corbeille interne et "
                "resteront restaurables.\n\n"
                "Continuer ?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        trash_root = root / "corbeille"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch = trash_root / f"{batch_prefix}_{timestamp}"
        suffix = 1

        while batch.exists():
            batch = trash_root / f"{batch_prefix}_{timestamp}_{suffix}"
            suffix += 1

        batch.mkdir(
            parents=True,
            exist_ok=False,
        )

        moved: list[tuple[Path, Path]] = []
        relative_folders: list[str] = []
        identifiers: set[str] = set()

        original_index = list(
            getattr(
                self.project,
                index_attribute,
                [],
            )
        )

        try:
            for source_folder in folders:
                relative_folder = (
                    source_folder.relative_to(root).as_posix()
                )
                destination = batch / relative_folder
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                identifier = self._definition_identifier(
                    source_folder / definition_name
                )

                if identifier:
                    identifiers.add(identifier)

                shutil.move(
                    str(source_folder),
                    str(destination),
                )
                moved.append(
                    (source_folder, destination)
                )
                relative_folders.append(relative_folder)

            retained_index = [
                summary
                for summary in original_index
                if str(
                    summary.get("identifiant", "")
                ).strip() not in identifiers
            ]

            removed_index = [
                summary
                for summary in original_index
                if summary not in retained_index
            ]

            manifest = {
                "type": manifest_type,
                "date": datetime.now().isoformat(),
                "projet": str(
                    getattr(self.project, "name", "")
                ),
                "dossiers": relative_folders,
                "index_retires": removed_index,
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
                setattr(
                    self.project,
                    index_attribute,
                    retained_index,
                )

                try:
                    self.project.save()
                except Exception:
                    setattr(
                        self.project,
                        index_attribute,
                        original_index,
                    )
                    raise

        except Exception as exc:
            setattr(
                self.project,
                index_attribute,
                original_index,
            )

            for source_folder, destination in reversed(moved):
                try:
                    source_folder.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_folder),
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
                    "Les contenus n’ont pas pu être déplacés "
                    f"correctement.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(relative_folders)} {item_label} placée(s) dans la corbeille."
        )

        messagebox.showinfo(
            "Contenus déplacés",
            (
                f"{len(relative_folders)} {item_label} ont été placées "
                "dans la corbeille interne.\n"
                "Elles restent restaurables."
            ),
            parent=self,
        )

    def restore_latest_content_sheets(
        self,
        batch: Path | None = None,
    ) -> None:
        self._restore_content_batch(
            batch=batch,
            batch_prefix="fiches_contenu_",
            index_attribute="content_sheets",
            item_label="fiche(s) de contenu",
        )

    def restore_latest_content_collections(
        self,
        batch: Path | None = None,
    ) -> None:
        self._restore_content_batch(
            batch=batch,
            batch_prefix="collections_contenu_",
            index_attribute="content_collections",
            item_label="collection(s) de contenu",
        )

    def _restore_content_batch(
        self,
        *,
        batch: Path | None,
        batch_prefix: str,
        index_attribute: str,
        item_label: str,
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
            batch = self._find_latest_trash_batch(
                root,
                batch_prefix,
            )

        if batch is None:
            messagebox.showinfo(
                "Aucun contenu à restaurer",
                f"La corbeille ne contient aucune {item_label}.",
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

        folders = manifest.get("dossiers", [])
        removed_index = manifest.get("index_retires", [])

        if not isinstance(folders, list) or not folders:
            messagebox.showerror(
                "Restauration impossible",
                "Le lot ne contient aucun dossier exploitable.",
                parent=self,
            )
            return

        confirmed = messagebox.askyesno(
            "Restaurer les contenus",
            (
                f"{len(folders)} {item_label} seront replacées dans "
                "la bibliothèque du projet.\n\n"
                "Confirmer la restauration ?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        active_index = list(
            getattr(
                self.project,
                index_attribute,
                [],
            )
        )
        restored: list[tuple[Path, Path]] = []
        path_mapping: dict[str, str] = {}

        try:
            for value in folders:
                original_relative = str(value).strip()

                if not original_relative:
                    continue

                source_folder = batch / original_relative

                if not source_folder.is_dir():
                    raise FileNotFoundError(
                        "Dossier absent dans la corbeille : "
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
                    str(source_folder),
                    str(destination),
                )
                restored.append(
                    (source_folder, destination)
                )

            restored_index: list[dict] = []

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

            setattr(
                self.project,
                index_attribute,
                combined_index,
            )

            try:
                self.project.save()
            except Exception:
                setattr(
                    self.project,
                    index_attribute,
                    active_index,
                )
                raise

            shutil.rmtree(batch)

        except Exception as exc:
            setattr(
                self.project,
                index_attribute,
                active_index,
            )

            for source_folder, destination in reversed(restored):
                try:
                    source_folder.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_folder),
                        )
                except Exception:
                    pass

            messagebox.showerror(
                "Restauration incomplète",
                (
                    "Les contenus n’ont pas pu être restaurés "
                    f"correctement.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(restored)} {item_label} restaurée(s)."
        )

        messagebox.showinfo(
            "Contenus restaurés",
            (
                f"{len(restored)} {item_label} ont été replacées dans "
                "la bibliothèque du projet."
            ),
            parent=self,
        )

    @staticmethod
    def _find_latest_trash_batch(
        root: Path,
        prefix: str,
    ) -> Path | None:
        trash_root = root / "corbeille"

        if not trash_root.exists():
            return None

        try:
            candidates = [
                item
                for item in trash_root.iterdir()
                if (
                    item.is_dir()
                    and item.name.startswith(prefix)
                    and (item / "manifest.json").is_file()
                )
            ]
        except OSError:
            return None

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda item: item.name,
        )

    def _find_latest_trash_content_sheets(
        self,
        root: Path,
    ) -> Path | None:
        return self._find_latest_trash_batch(
            root,
            "fiches_contenu_",
        )

    def _find_latest_trash_content_collections(
        self,
        root: Path,
    ) -> Path | None:
        return self._find_latest_trash_batch(
            root,
            "collections_contenu_",
        )

    def show_unused_content_sheets_details(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        sheets, _ = self._find_unused_content_sheets(root)

        if not sheets:
            messagebox.showinfo(
                "Aucune fiche inutilisée",
                (
                    "Toutes les fiches de contenu sont associées à une "
                    "collection, une page ou une production."
                ),
                parent=self,
            )
            self.analyze()
            return

        CleanupDetailsDialog(
            parent=self,
            title="Fiches de contenu non utilisées",
            project_root=root,
            files=sheets,
            dependency_text=(
                "aucune collection, page ou production associée"
            ),
        )

    def show_unused_content_collections_details(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        collections, _ = self._find_unused_content_collections(root)

        if not collections:
            messagebox.showinfo(
                "Aucune collection inutilisée",
                (
                    "Toutes les collections sont associées à une "
                    "production."
                ),
                parent=self,
            )
            self.analyze()
            return

        CleanupDetailsDialog(
            parent=self,
            title="Collections non utilisées",
            project_root=root,
            files=collections,
            dependency_text="aucune production associée",
        )

    def move_unused_models_to_trash(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        models, _ = self._find_unused_models(root)

        if not models:
            messagebox.showinfo(
                "Aucun modèle inutilisé",
                "Aucun modèle inutilisé n’a été détecté.",
                parent=self,
            )
            self.analyze()
            return

        confirmed = messagebox.askyesno(
            "Mettre les modèles à la corbeille",
            (
                f"{len(models)} modèle(s) ne sont associés à aucune page, "
                "fiche, collection ou production.\n\n"
                "Ils seront déplacés dans la corbeille interne du projet "
                "et resteront restaurables.\n\n"
                "Continuer ?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        trash_root = root / "corbeille"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch = trash_root / f"modeles_{timestamp}"
        suffix = 1

        while batch.exists():
            batch = trash_root / f"modeles_{timestamp}_{suffix}"
            suffix += 1

        batch.mkdir(
            parents=True,
            exist_ok=False,
        )

        moved: list[tuple[Path, Path]] = []
        relative_folders: list[str] = []
        model_ids: set[str] = set()

        original_index = list(
            getattr(
                self.project,
                "models",
                [],
            )
        )

        try:
            for source_folder in models:
                relative_folder = (
                    source_folder.relative_to(root).as_posix()
                )
                destination = batch / relative_folder
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                model_file = source_folder / "modele.json"

                try:
                    with model_file.open(
                        "r",
                        encoding="utf-8-sig",
                    ) as handle:
                        data = json.load(handle)
                except (
                    OSError,
                    UnicodeError,
                    json.JSONDecodeError,
                ):
                    data = {}

                identity = data.get("identite", {})

                if isinstance(identity, dict):
                    identifier = str(
                        identity.get("identifiant", "")
                    ).strip()

                    if identifier:
                        model_ids.add(identifier)

                shutil.move(
                    str(source_folder),
                    str(destination),
                )
                moved.append(
                    (source_folder, destination)
                )
                relative_folders.append(relative_folder)

            retained_index = [
                summary
                for summary in original_index
                if str(
                    summary.get("identifiant", "")
                ).strip() not in model_ids
            ]

            removed_index = [
                summary
                for summary in original_index
                if summary not in retained_index
            ]

            manifest = {
                "type": "modeles",
                "date": datetime.now().isoformat(),
                "projet": str(
                    getattr(self.project, "name", "")
                ),
                "dossiers": relative_folders,
                "index_retires": removed_index,
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
                self.project.models = retained_index

                try:
                    self.project.save()
                except Exception:
                    self.project.models = original_index
                    raise

        except Exception as exc:
            self.project.models = original_index

            for source_folder, destination in reversed(moved):
                try:
                    source_folder.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_folder),
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
                    "Les modèles n’ont pas pu être déplacés "
                    f"correctement.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(relative_folders)} modèle(s) placé(s) dans la corbeille."
        )

        messagebox.showinfo(
            "Modèles déplacés",
            (
                f"{len(relative_folders)} modèle(s) ont été placés dans "
                "la corbeille interne.\n"
                "Ils restent restaurables."
            ),
            parent=self,
        )

    def restore_latest_models(
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
            batch = self._find_latest_trash_models(root)

        if batch is None:
            messagebox.showinfo(
                "Aucun modèle à restaurer",
                "La corbeille ne contient aucun lot de modèles.",
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

        folders = manifest.get("dossiers", [])
        removed_index = manifest.get("index_retires", [])

        if not isinstance(folders, list) or not folders:
            messagebox.showerror(
                "Restauration impossible",
                "Le lot ne contient aucun modèle exploitable.",
                parent=self,
            )
            return

        confirmed = messagebox.askyesno(
            "Restaurer les modèles",
            (
                f"{len(folders)} modèle(s) seront replacés dans la "
                "bibliothèque du projet.\n\n"
                "Confirmer la restauration ?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        active_index = list(
            getattr(
                self.project,
                "models",
                [],
            )
        )
        restored: list[tuple[Path, Path]] = []
        path_mapping: dict[str, str] = {}

        try:
            for value in folders:
                original_relative = str(value).strip()

                if not original_relative:
                    continue

                source_folder = batch / original_relative

                if not source_folder.is_dir():
                    raise FileNotFoundError(
                        "Modèle absent dans la corbeille : "
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
                    str(source_folder),
                    str(destination),
                )
                restored.append(
                    (source_folder, destination)
                )

            restored_index: list[dict] = []

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

            self.project.models = combined_index

            try:
                self.project.save()
            except Exception:
                self.project.models = active_index
                raise

            shutil.rmtree(batch)

        except Exception as exc:
            self.project.models = active_index

            for source_folder, destination in reversed(restored):
                try:
                    source_folder.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    if destination.exists():
                        shutil.move(
                            str(destination),
                            str(source_folder),
                        )
                except Exception:
                    pass

            messagebox.showerror(
                "Restauration incomplète",
                (
                    "Les modèles n’ont pas pu être restaurés "
                    f"correctement.\n\n{exc}"
                ),
                parent=self,
            )
            self.analyze()
            return

        self.analyze()
        self.status_var.set(
            f"{len(restored)} modèle(s) restauré(s)."
        )

        messagebox.showinfo(
            "Modèles restaurés",
            (
                f"{len(restored)} modèle(s) ont été replacés dans "
                "la bibliothèque du projet."
            ),
            parent=self,
        )

    @staticmethod
    def _find_latest_trash_models(
        root: Path,
    ) -> Path | None:
        trash_root = root / "corbeille"

        if not trash_root.exists():
            return None

        try:
            candidates = [
                item
                for item in trash_root.iterdir()
                if (
                    item.is_dir()
                    and item.name.startswith("modeles_")
                    and (item / "manifest.json").is_file()
                )
            ]
        except OSError:
            return None

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda item: item.name,
        )

    def show_unused_models_details(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

        models, _ = self._find_unused_models(root)

        if not models:
            messagebox.showinfo(
                "Aucun modèle inutilisé",
                (
                    "Tous les modèles du projet sont associés à une page, "
                    "une fiche, une collection ou une production."
                ),
                parent=self,
            )
            self.analyze()
            return

        CleanupDetailsDialog(
            parent=self,
            title="Modèles non utilisés",
            project_root=root,
            files=models,
            dependency_text=(
                "aucune page, fiche, collection ou production associée"
            ),
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

    def _find_unused_content_sheets(
        self,
        root: Path,
    ) -> tuple[list[Path], int]:
        used_ids = self._used_content_sheet_ids(root)
        sheets_folder = root / "contenus" / "fiches"

        return self._find_unused_content_folders(
            folder=sheets_folder,
            definition_name="fiche.json",
            used_ids=used_ids,
        )

    def _find_unused_content_collections(
        self,
        root: Path,
    ) -> tuple[list[Path], int]:
        used_ids = self._used_content_collection_ids(root)
        collections_folder = root / "contenus" / "collections"

        return self._find_unused_content_folders(
            folder=collections_folder,
            definition_name="collection.json",
            used_ids=used_ids,
        )

    def _find_unused_content_folders(
        self,
        *,
        folder: Path,
        definition_name: str,
        used_ids: set[str],
    ) -> tuple[list[Path], int]:
        unused: list[Path] = []
        total_size = 0

        if not folder.exists():
            return unused, total_size

        try:
            candidates = [
                item
                for item in folder.iterdir()
                if (
                    item.is_dir()
                    and (item / definition_name).is_file()
                )
            ]
        except OSError:
            return unused, total_size

        for candidate in candidates:
            identifier = self._definition_identifier(
                candidate / definition_name
            )

            if not identifier or identifier in used_ids:
                continue

            unused.append(candidate)
            _, folder_size = self._folder_stats(candidate)
            total_size += folder_size

        unused.sort(
            key=lambda path: str(path).casefold()
        )

        return unused, total_size

    @staticmethod
    def _definition_identifier(
        definition_file: Path,
    ) -> str:
        try:
            with definition_file.open(
                "r",
                encoding="utf-8-sig",
            ) as handle:
                data = json.load(handle)
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
        ):
            return ""

        identity = data.get("identite", {})

        if not isinstance(identity, dict):
            return ""

        return str(
            identity.get("identifiant", "")
        ).strip()

    def _used_content_sheet_ids(
        self,
        root: Path,
    ) -> set[str]:
        identifiers: set[str] = set()

        collections_folder = root / "contenus" / "collections"

        if collections_folder.exists():
            try:
                collection_files = list(
                    collections_folder.rglob("collection.json")
                )
            except OSError:
                collection_files = []

            for collection_file in collection_files:
                try:
                    with collection_file.open(
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

                sheets = data.get("fiches", [])

                if not isinstance(sheets, list):
                    continue

                for entry in sheets:
                    if not isinstance(entry, dict):
                        continue

                    identifier = str(
                        entry.get("identifiant", "")
                    ).strip()

                    if identifier:
                        identifiers.add(identifier)

        self._collect_named_identifiers_from_roots(
            roots=(
                root / "projet.json",
                root / "documents",
                root / "productions",
            ),
            accepted_keys={
                "contenu",
                "fiche",
                "fiche_id",
                "fiche_identifiant",
                "source_content_id",
            },
            destination=identifiers,
        )

        return identifiers

    def _used_content_collection_ids(
        self,
        root: Path,
    ) -> set[str]:
        identifiers: set[str] = set()

        self._collect_named_identifiers_from_roots(
            roots=(
                root / "projet.json",
                root / "documents",
                root / "productions",
            ),
            accepted_keys={
                "collection",
                "collection_id",
                "collection_identifiant",
                "source_collection_id",
            },
            destination=identifiers,
        )

        return identifiers

    def _collect_named_identifiers_from_roots(
        self,
        *,
        roots: tuple[Path, ...],
        accepted_keys: set[str],
        destination: set[str],
    ) -> None:
        for search_root in roots:
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

                self._collect_named_identifiers(
                    data,
                    accepted_keys,
                    destination,
                )

    @staticmethod
    def _collect_named_identifiers(
        value,
        accepted_keys: set[str],
        destination: set[str],
    ) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized_key = str(key).strip().casefold()

                if (
                    normalized_key in accepted_keys
                    and isinstance(child, str)
                ):
                    identifier = child.strip()

                    if identifier:
                        destination.add(identifier)

                ProjectCleanupDialog._collect_named_identifiers(
                    child,
                    accepted_keys,
                    destination,
                )
            return

        if isinstance(value, list):
            for child in value:
                ProjectCleanupDialog._collect_named_identifiers(
                    child,
                    accepted_keys,
                    destination,
                )

    def _find_unused_models(
        self,
        root: Path,
    ) -> tuple[list[Path], int]:
        used_ids = self._used_model_ids(root)
        models_folder = root / "modeles"
        unused: list[Path] = []
        total_size = 0

        if not models_folder.exists():
            return unused, total_size

        try:
            candidates = [
                item
                for item in models_folder.iterdir()
                if (
                    item.is_dir()
                    and (item / "modele.json").is_file()
                )
            ]
        except OSError:
            return unused, total_size

        for folder in candidates:
            model_file = folder / "modele.json"

            try:
                with model_file.open(
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

            identity = data.get("identite", {})

            if not isinstance(identity, dict):
                continue

            identifier = str(
                identity.get("identifiant", "")
            ).strip()

            if not identifier or identifier in used_ids:
                continue

            unused.append(folder)
            _, folder_size = self._folder_stats(folder)
            total_size += folder_size

        unused.sort(
            key=lambda path: str(path).casefold()
        )

        return unused, total_size

    def _used_model_ids(
        self,
        root: Path,
    ) -> set[str]:
        identifiers: set[str] = set()
        project_model_id = str(
            getattr(
                self.project,
                "book_model_id",
                "",
            )
        ).strip()

        if project_model_id:
            identifiers.add(project_model_id)

        search_roots = (
            root / "projet.json",
            root / "documents",
            root / "contenus",
            root / "productions",
        )

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

                self._collect_model_reference_ids(
                    data,
                    identifiers,
                )

        return identifiers

    @staticmethod
    def _collect_model_reference_ids(
        value,
        destination: set[str],
    ) -> None:
        model_keys = {
            "book_model",
            "modele",
            "modele_identifiant",
            "modele_prefere",
            "source_model_id",
        }

        if isinstance(value, dict):
            for key, child in value.items():
                normalized_key = str(key).strip().casefold()

                if (
                    normalized_key in model_keys
                    and isinstance(child, str)
                ):
                    identifier = child.strip()

                    if identifier:
                        destination.add(identifier)

                ProjectCleanupDialog._collect_model_reference_ids(
                    child,
                    destination,
                )
            return

        if isinstance(value, list):
            for child in value:
                ProjectCleanupDialog._collect_model_reference_ids(
                    child,
                    destination,
                )

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
    # Vue intégrée
    # ==========================================================

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        callback = self.on_close

        if callback is not None:
            callback()
            return

        try:
            self.destroy()
        except tk.TclError:
            pass