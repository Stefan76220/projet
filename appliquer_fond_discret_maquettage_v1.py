from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
BACKGROUND = PROJECT / "assets" / "interface" / "backgrounds" / "editorial_bg_soft.png"

EXPECTED_SHA256 = '001a2e07ddd35f9fbea536af658fcd452f44dde8b7581ccb3a5442b8b50bfbb7'
REQUIRED_MARKER = "RUBAN_PAINT_SANS_MINIATURES_V1"
NEW_MARKER = "FOND_DISCRET_MAQUETTAGE_V1"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_method(source: str, name: str, new_block: str) -> str:
    lines = source.splitlines(keepends=True)
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


NEW_SHOW = r"""    def show(self) -> None:
        self._deactivate_global_shortcuts()
        self._clear_parent()

        # Les références aux widgets appartiennent à l'écran courant.
        self._page_type_buttons.clear()
        self._page_type_button_states.clear()
        self._selection_controls_cache = None
        self._summary_text_cache = None
        self._progress_text_cache = None
        self._sequence_row_widgets.clear()
        self._sequence_row_signatures.clear()
        self._rendered_selected_page_ids.clear()
        self._sequence_empty_label = None

        # FOND_DISCRET_MAQUETTAGE_V1
        # Le fond léger de l'accueil est posé derrière tout le Bureau de
        # maquettage. Les panneaux existants restent inchangés par-dessus.
        self._root = ctk.CTkFrame(
            self.parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        self._root.pack(fill="both", expand=True)
        self._root.grid_columnconfigure(0, weight=1)
        self._root.grid_rowconfigure(2, weight=1)
        self._root.bind("<Destroy>", self._on_root_destroyed, add="+")
        self._activate_global_shortcuts()

        self._mockup_background_label = None
        self._mockup_background_source = None
        self._mockup_background_photo = None

        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_soft.png"
        )
        if background_path.is_file():
            try:
                from PIL import Image, ImageTk

                self._mockup_background_source = Image.open(background_path).convert("RGB")

                bg_label = tk.Label(
                    self._root,
                    borderwidth=0,
                    highlightthickness=0,
                    background=self.WINDOW_BG,
                )
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                bg_label.lower()
                self._mockup_background_label = bg_label

                def redraw_background(_event=None) -> None:
                    label = self._mockup_background_label
                    source = self._mockup_background_source
                    if label is None or source is None:
                        return
                    try:
                        width = max(1, int(self._root.winfo_width()))
                        height = max(1, int(self._root.winfo_height()))
                        if width <= 2 or height <= 2:
                            return

                        source_ratio = source.width / source.height
                        target_ratio = width / height
                        if target_ratio > source_ratio:
                            new_width = width
                            new_height = max(1, int(round(width / source_ratio)))
                        else:
                            new_height = height
                            new_width = max(1, int(round(height * source_ratio)))

                        resized = source.resize(
                            (new_width, new_height),
                            Image.Resampling.LANCZOS,
                        )

                        left = max(0, (new_width - width) // 2)
                        top = max(0, (new_height - height) // 2)
                        cropped = resized.crop(
                            (left, top, left + width, top + height)
                        )

                        photo = ImageTk.PhotoImage(cropped)
                        self._mockup_background_photo = photo
                        label.configure(image=photo)
                    except Exception:
                        pass

                self._root.bind(
                    "<Configure>",
                    redraw_background,
                    add="+",
                )
                self._root.after_idle(redraw_background)
            except Exception:
                # Le Bureau reste parfaitement utilisable avec son fond uni.
                self._mockup_background_label = None
                self._mockup_background_source = None
                self._mockup_background_photo = None

        self._create_header(self._root).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(6, 4),
        )

        self._ribbon_frame = self._create_ribbon(self._root)
        self._ribbon_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 8),
        )

        self._create_sequence_panel(self._root).grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 10),
        )

        self._refresh_sequence()"""


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    if not BACKGROUND.is_file():
        fail(f"fond discret introuvable : {BACKGROUND}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("FOND_DISCRET_MAQUETTAGE_DEJA_APPLIQUE")
        return

    if REQUIRED_MARKER not in original:
        fail(
            "la version validée du ruban Paint n'est pas détectée. "
            "Par sécurité, aucune modification n'est appliquée."
        )

    current_hash = sha256(TARGET)
    if current_hash != EXPECTED_SHA256:
        fail(
            "mockup_view.py n'est plus exactement la version que vous venez "
            "de transmettre. Par sécurité, aucune modification n'est appliquée. "
            f"SHA256 actuel : {current_hash}"
        )

    candidate = replace_method(original, "show", NEW_SHOW)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_fond_discret_{stamp}.py"
    temporary = TARGET.with_suffix(".fond_discret.tmp")

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

    print("FOND_DISCRET_MAQUETTAGE_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Fond utilisé : assets/interface/backgrounds/editorial_bg_soft.png")
    print("Le fond est appliqué uniquement au Bureau de maquettage.")
    print("Ruban, Plan du livre et logique fonctionnelle : inchangés.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
