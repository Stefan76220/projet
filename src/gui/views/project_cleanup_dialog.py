from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
from typing import Callable
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts


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

        self.title("Nettoyage de la base")
        self.geometry("900x700")
        self.minsize(840, 640)
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
        container.grid_rowconfigure(3, weight=1)

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
        self.move_cache_button.configure(
            state="normal" if self._cache_file_count > 0 else "disabled"
        )

        self._latest_trash_cache = self._find_latest_trash_cache(root)
        self.restore_cache_button.configure(
            state="normal" if self._latest_trash_cache is not None else "disabled"
        )

        self._trash_file_count, self._trash_size = self._folder_stats(
            root / "corbeille"
        )
        self.empty_trash_button.configure(
            state="normal" if self._trash_file_count > 0 else "disabled"
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
        else:
            self.status_var.set("Le cache et la corbeille du projet sont vides.")

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

    def restore_latest_cache(self) -> None:
        root = self._project_root()

        if root is None or not root.exists():
            messagebox.showerror(
                "Projet indisponible",
                "Le dossier du projet est introuvable.",
                parent=self,
            )
            return

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