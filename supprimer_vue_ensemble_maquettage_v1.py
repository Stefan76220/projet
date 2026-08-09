from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
EXPECTED_SHA256 = 'b7d290ee3631b0a146233a8be0fbcc16bac7d49731418d319c61c0f8b41a35e5'
NEW_MARKER = "APERCU_MAQUETTAGE_GRANDE_VUE_SEULE_V1"

NEW_OPEN_PREVIEW = '    def _open_preview(self) -> None:\n        if self._preview_window is not None:\n            try:\n                if self._preview_window.winfo_exists():\n                    self._preview_window.focus_force()\n                    self._preview_window.lift()\n                    return\n            except Exception:\n                self._preview_window = None\n\n        window = ctk.CTkToplevel(self.parent)\n        self._preview_window = window\n        window.title("Projet envisagé")\n\n        # APERCU_GRANDE_VUE_V3\n        # APERCU_MAQUETTAGE_GRANDE_VUE_SEULE_V1\n        # APERCU_FENETRE_CENTREE_V1\n        # Fenêtre resserrée autour du livre : elle reste redimensionnable.\n        preview_width = 840\n        preview_height = 650\n        window.minsize(740, 560)\n        window.update_idletasks()\n\n        screen_width = int(window.winfo_screenwidth())\n        screen_height = int(window.winfo_screenheight())\n        pos_x = max(0, (screen_width - preview_width) // 2)\n        pos_y = max(0, (screen_height - preview_height) // 2)\n\n        window.geometry(\n            f"{preview_width}x{preview_height}+{pos_x}+{pos_y}"\n        )\n        window.configure(fg_color=self.WINDOW_BG)\n        window.protocol("WM_DELETE_WINDOW", self._close_preview)\n        window.grid_columnconfigure(0, weight=1)\n        window.grid_rowconfigure(2, weight=1)\n        window.bind("<Left>", lambda _event: self._show_previous_spread())\n        window.bind("<Right>", lambda _event: self._show_next_spread())\n\n        self._preview_animating = False\n        self._preview_turn_photo = None\n\n        header = ctk.CTkFrame(window, fg_color="transparent", height=32)\n        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 4))\n        header.grid_columnconfigure(0, weight=1)\n        header.grid_propagate(False)\n\n        ctk.CTkLabel(\n            header,\n            text="Projet envisagé",\n            font=Fonts.H2,\n            text_color=self.INK,\n        ).grid(row=0, column=0, sticky="w")\n\n        ctk.CTkLabel(\n            header,\n            text=self._preview_summary_text(),\n            font=Fonts.SMALL,\n            text_color=self.TEXT_MUTED,\n        ).grid(row=0, column=1, sticky="e")\n\n        # Canvas = fond stable. Il ne repasse jamais devant les outils.\n        ribbon = self._create_preview_background_canvas(\n            window,\n            fixed_height=68,\n        )\n        ribbon.grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=12,\n            pady=(0, 8),\n        )\n        ribbon.grid_propagate(False)\n\n        controls_row = ctk.CTkFrame(\n            ribbon,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        controls_row.place(relx=0.5, rely=0.5, anchor="center")\n\n        def preview_group(\n            title: str,\n            width: int,\n            accent: str,\n        ) -> tuple[ctk.CTkFrame, ctk.CTkFrame]:\n            group_soft = self._mix_color_with_white(accent, 0.91)\n            title_soft = self._mix_color_with_white(accent, 0.84)\n\n            group = ctk.CTkFrame(\n                controls_row,\n                width=width,\n                height=60,\n                fg_color=group_soft,\n                corner_radius=5,\n                border_width=1,\n                border_color=title_soft,\n            )\n            group.pack(side="left", fill="y", padx=2, pady=4)\n            group.pack_propagate(False)\n\n            controls = ctk.CTkFrame(\n                group,\n                fg_color="transparent",\n                height=40,\n            )\n            controls.pack(fill="x", padx=3, pady=(2, 0))\n            controls.pack_propagate(False)\n\n            title_bar = ctk.CTkFrame(\n                group,\n                height=16,\n                fg_color=title_soft,\n                corner_radius=0,\n            )\n            title_bar.pack(side="bottom", fill="x", padx=1, pady=(0, 1))\n            title_bar.pack_propagate(False)\n\n            ctk.CTkLabel(\n                title_bar,\n                text=title,\n                font=(Fonts.FAMILY, 9, "bold"),\n                text_color=accent,\n            ).place(relx=0, rely=0, relwidth=1, relheight=1)\n            return group, controls\n\n        def preview_button(\n            parent_frame,\n            icon: str,\n            label: str,\n            command,\n            width: int = 66,\n            accent: str | None = None,\n        ) -> ctk.CTkButton:\n            text_color = accent or self.INK\n            border = self._mix_color_with_white(text_color, 0.55)\n            button = ctk.CTkButton(\n                parent_frame,\n                text=f"{icon}\\n{label}",\n                width=width,\n                height=39,\n                corner_radius=5,\n                fg_color=self.GROUP_BG,\n                hover_color=self.ACCENT_SOFT,\n                text_color=text_color,\n                border_width=1,\n                border_color=border,\n                font=(Fonts.FAMILY, 9),\n                command=command,\n            )\n            button.pack(side="left", padx=1, pady=0)\n            return button\n\n        _, navigation_controls = preview_group(\n            "Navigation",\n            140,\n            self.SKY,\n        )\n        self._preview_previous_button = preview_button(\n            navigation_controls,\n            "◀",\n            "Précédent",\n            self._show_previous_spread,\n        )\n        self._preview_next_button = preview_button(\n            navigation_controls,\n            "▶",\n            "Suivant",\n            self._show_next_spread,\n        )\n\n        _, window_controls = preview_group(\n            "Fenêtre",\n            72,\n            self.CORAL,\n        )\n        preview_button(\n            window_controls,\n            "×",\n            "Fermer",\n            self._close_preview,\n            width=66,\n            accent=self.CORAL,\n        )\n\n        self._preview_body = self._create_preview_background_canvas(window)\n        self._preview_body.grid(\n            row=2,\n            column=0,\n            sticky="nsew",\n            padx=12,\n            pady=(0, 5),\n        )\n        self._preview_body.grid_columnconfigure(0, weight=1)\n        self._preview_body.grid_rowconfigure(0, weight=1)\n\n        self._preview_nav = ctk.CTkFrame(\n            window,\n            fg_color=self.GROUP_BG,\n            corner_radius=6,\n            height=28,\n            border_width=1,\n            border_color=self.BORDER,\n        )\n        self._preview_nav.grid(\n            row=3,\n            column=0,\n            sticky="ew",\n            padx=12,\n            pady=(0, 8),\n        )\n        self._preview_nav.grid_columnconfigure(0, weight=1)\n        self._preview_nav.grid_propagate(False)\n\n        self._preview_position_label = ctk.CTkLabel(\n            self._preview_nav,\n            text="",\n            font=Fonts.SMALL,\n            text_color=self.INK,\n        )\n        self._preview_position_label.grid(row=0, column=0)\n\n        self._preview_spreads = self._build_preview_spreads(\n            list(self._items())\n        )\n        self._preview_index = 0\n        self._preview_mode = "large"\n        self._preview_large_button = None\n        self._preview_overview_button = None\n        self._render_preview_current_spread()\n        window.after(100, window.focus_force)\n\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_method(source_text: str, name: str, new_block: str) -> str:
    lines = source_text.splitlines(keepends=True)
    start = None
    for index, line in enumerate(lines):
        if line.startswith(f"    def {name}("):
            start = index
            break
    if start is None:
        fail(f"méthode {name} introuvable")

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("    def ") or lines[index].startswith("    @"):
            end = index
            break

    return "".join(lines[:start]) + new_block.rstrip() + "\n\n" + "".join(lines[end:])


def remove_method(source_text: str, name: str) -> str:
    lines = source_text.splitlines(keepends=True)
    start = None
    for index, line in enumerate(lines):
        if line.startswith(f"    def {name}("):
            start = index
            break
    if start is None:
        fail(f"méthode {name} introuvable")

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("    def ") or lines[index].startswith("    @"):
            end = index
            break

    return "".join(lines[:start]) + "".join(lines[end:])


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("MAQUETTAGE_GRANDE_VUE_SEULE_DEJA_APPLIQUE")
        return

    current_hash = sha256(TARGET)
    if current_hash != EXPECTED_SHA256:
        fail(
            "mockup_view.py n'est plus exactement la version transmise. "
            "Par sécurité, aucune modification n'est appliquée. "
            f"SHA256 actuel : {current_hash}"
        )

    required = (
        "APERCU_GRANDE_VUE_V3",
        "APERCU_ROTATION_ALIGNEE_V1",
        "APERCU_FENETRE_CENTREE_V1",
        "APERCU_ENSEMBLE_REALISTE_V1",
    )
    missing = [marker for marker in required if marker not in original]
    if missing:
        fail("version attendue non détectée : " + ", ".join(missing))

    candidate = replace_method(
        original,
        "_open_preview",
        NEW_OPEN_PREVIEW,
    )

    for method_name in (
        "_set_preview_mode",
        "_render_preview_overview",
        "_create_preview_spread",
        "_create_preview_page",
    ):
        candidate = remove_method(candidate, method_name)

    forbidden = (
        'text="Ensemble"',
        '"overview"',
        "def _render_preview_overview(",
        "def _create_preview_spread(",
        "def _create_preview_page(",
    )
    remaining = [item for item in forbidden if item in candidate]
    if remaining:
        fail("nettoyage incomplet : " + ", ".join(remaining))

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"mockup_view_avant_suppression_vue_ensemble_{stamp}.py"
    )
    temporary = TARGET.with_suffix(".grande_vue_seule.tmp")

    try:
        temporary.write_text(candidate, encoding="utf-8")
        py_compile.compile(str(temporary), doraise=True)
        shutil.copy2(TARGET, backup)
        temporary.replace(TARGET)
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        try:
            temporary.unlink(missing_ok=True)
        except Exception:
            pass
        if backup.exists():
            shutil.copy2(backup, TARGET)
        fail(f"installation annulée automatiquement : {exc}")

    print("MAQUETTAGE_GRANDE_VUE_SEULE_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Aperçu : Vue Ensemble supprimée.")
    print("Grande vue : conservée seule, avec animation et réglages validés.")
    print("Ruban de l'Aperçu : uniquement Navigation + Fermer.")
    print("Pagination et recto-verso : inchangés.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
