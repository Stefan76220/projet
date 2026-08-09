from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
BACKGROUND = PROJECT / "assets" / "interface" / "backgrounds" / "editorial_bg_soft.png"

REQUIRED_MARKERS = (
    "FOND_DISCRET_MAQUETTAGE_V1",
    "FOND_DISCRET_PLAN_LIVRE_V1",
    "FOND_DISCRET_SURFACE_MAX_V1",
)
NEW_MARKER = "FOND_VISIBLE_RUBAN_PLAN_V1"

NEW_PLAN_REFRESH = '    def _refresh_plan_background(self, _event=None) -> None:\n        """Affiche le décor sur toute la surface libre derrière les cartes."""\n        frame = self._sequence_frame\n        label = getattr(self, "_plan_background_label", None)\n        source = getattr(self, "_plan_background_source", None)\n        if frame is None or label is None or source is None:\n            return\n\n        try:\n            from PIL import Image, ImageTk\n\n            width = max(1, int(frame.winfo_width()))\n            height = max(1, int(frame.winfo_height()))\n            if width <= 2 or height <= 2:\n                return\n\n            source_ratio = source.width / source.height\n            target_ratio = width / height\n            if target_ratio > source_ratio:\n                resize_width = width\n                resize_height = max(height, int(round(width / source_ratio)))\n            else:\n                resize_height = height\n                resize_width = max(width, int(round(height * source_ratio)))\n\n            resized = source.resize(\n                (resize_width, resize_height),\n                Image.Resampling.LANCZOS,\n            )\n            left = max(0, (resize_width - width) // 2)\n            top = max(0, (resize_height - height) // 2)\n            cropped = resized.crop((left, top, left + width, top + height))\n\n            photo = ImageTk.PhotoImage(cropped)\n            self._plan_background_photo = photo\n            label.configure(image=photo)\n            label.place(x=0, y=0, width=width, height=height)\n\n            label.lift()\n            for record in self._sequence_row_widgets.values():\n                row = record.get("row")\n                if row is not None:\n                    try:\n                        row.lift()\n                    except Exception:\n                        pass\n\n            if self._sequence_empty_label is not None:\n                try:\n                    self._sequence_empty_label.lift()\n                except Exception:\n                    pass\n        except Exception:\n            try:\n                label.place_forget()\n            except Exception:\n                pass\n'
NEW_RIBBON_CONTAINER_HELPER = '    def _create_soft_background_container(self, parent):\n        """Conteneur Tk affichant réellement le décor léger en arrière-plan."""\n        container = tk.Label(\n            parent,\n            image="",\n            text="",\n            borderwidth=0,\n            highlightthickness=0,\n            background=self.RIBBON_BG,\n        )\n        container._soft_background_source = None\n        container._soft_background_photo = None\n\n        background_path = (\n            Path(__file__).resolve().parents[3]\n            / "assets"\n            / "interface"\n            / "backgrounds"\n            / "editorial_bg_soft.png"\n        )\n\n        if background_path.is_file():\n            try:\n                from PIL import Image, ImageTk\n\n                source = Image.open(background_path).convert("RGB")\n                container._soft_background_source = source\n\n                def redraw(_event=None) -> None:\n                    try:\n                        width = max(1, int(container.winfo_width()))\n                        height = max(1, int(container.winfo_height()))\n                        if width <= 2 or height <= 2:\n                            return\n\n                        source_ratio = source.width / source.height\n                        target_ratio = width / height\n                        if target_ratio > source_ratio:\n                            resize_width = width\n                            resize_height = max(\n                                height,\n                                int(round(width / source_ratio)),\n                            )\n                        else:\n                            resize_height = height\n                            resize_width = max(\n                                width,\n                                int(round(height * source_ratio)),\n                            )\n\n                        resized = source.resize(\n                            (resize_width, resize_height),\n                            Image.Resampling.LANCZOS,\n                        )\n                        left = max(0, (resize_width - width) // 2)\n                        top = max(0, (resize_height - height) // 2)\n                        cropped = resized.crop(\n                            (left, top, left + width, top + height)\n                        )\n                        photo = ImageTk.PhotoImage(cropped)\n                        container._soft_background_photo = photo\n                        container.configure(image=photo)\n                    except Exception:\n                        pass\n\n                container.bind("<Configure>", redraw, add="+")\n                container.after_idle(redraw)\n            except Exception:\n                pass\n\n        return container\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


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


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")
    if not BACKGROUND.is_file():
        fail(f"fond discret introuvable : {BACKGROUND}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("FOND_VISIBLE_RUBAN_PLAN_DEJA_APPLIQUE")
        return

    missing = [marker for marker in REQUIRED_MARKERS if marker not in original]
    if missing:
        fail("version attendue non détectée : " + ", ".join(missing))

    candidate = original

    candidate = replace_method(
        candidate,
        "_refresh_plan_background",
        NEW_PLAN_REFRESH,
    )

    old_row = """        row_height = 92
        card_height = 80
        row = tk.Frame(
            parent,
            height=row_height,
            background=self.RIBBON_BG,
            borderwidth=0,
            highlightthickness=0,
        )
        row.grid_columnconfigure(0, weight=0)
        row.grid_propagate(False)

        card_width = 820 if not automatic_blank else 700
        card_padx = (8, 6) if not automatic_blank else (54, 6)
"""
    new_row = """        row_height = 92
        card_height = 80
        card_width = 820 if not automatic_blank else 700
        card_padx = (8, 6) if not automatic_blank else (54, 6)
        row_width = card_width + (66 if automatic_blank else 18)

        row = tk.Frame(
            parent,
            width=row_width,
            height=row_height,
            background="#FBFAF6",
            borderwidth=0,
            highlightthickness=0,
        )
        row.grid_columnconfigure(0, weight=0)
        row.grid_propagate(False)
"""
    if old_row not in candidate:
        fail("structure des lignes de cartes introuvable")
    candidate = candidate.replace(old_row, new_row, 1)

    candidate = candidate.replace(
        """                    row.grid(
                        row=index,
                        column=0,
                        sticky="ew",
                        padx=4,
                        pady=3,
                    )""",
        """                    row.grid(
                        row=index,
                        column=0,
                        sticky="w",
                        padx=4,
                        pady=3,
                    )""",
        1,
    )
    candidate = candidate.replace(
        """                        record["row"].grid_configure(
                            row=index,
                            column=0,
                            sticky="ew",
                            padx=4,
                            pady=3,
                        )""",
        """                        record["row"].grid_configure(
                            row=index,
                            column=0,
                            sticky="w",
                            padx=4,
                            pady=3,
                        )""",
        1,
    )

    ribbon_anchor = "    def _create_ribbon(self, parent) -> ctk.CTkFrame:\n"
    if ribbon_anchor not in candidate:
        fail("méthode du ruban introuvable")
    candidate = candidate.replace(
        ribbon_anchor,
        NEW_RIBBON_CONTAINER_HELPER + "\n\n" + ribbon_anchor,
        1,
    )

    old_panel = """        self._ribbon_groups_panel = ctk.CTkFrame(
            ribbon,
            fg_color="transparent",
            corner_radius=0,
        )
"""
    new_panel = """        self._ribbon_groups_panel = self._create_soft_background_container(
            ribbon
        )
"""
    if old_panel not in candidate:
        fail("panneau principal du ruban introuvable")
    candidate = candidate.replace(old_panel, new_panel, 1)

    candidate = candidate.replace(
        "        self._install_ribbon_background(ribbon)\n",
        "",
        1,
    )

    marker_anchor = "        # FOND_DISCRET_SURFACE_MAX_V1\n"
    if marker_anchor not in candidate:
        fail("marqueur du fond précédent introuvable")
    candidate = candidate.replace(
        marker_anchor,
        marker_anchor + "        # FOND_VISIBLE_RUBAN_PLAN_V1\n",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_fond_visible_{stamp}.py"
    temporary = TARGET.with_suffix(".fond_visible.tmp")

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

    print("FOND_VISIBLE_RUBAN_PLAN_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Plan du livre : suppression des grands bandeaux gris entre les cartes.")
    print("Plan du livre : fond discret visible sur toute la surface libre.")
    print("Ruban : fond discret réellement affiché derrière groupes et outils.")
    print("Cartes, groupes colorés et outils restent au premier plan.")
    print("Aucune logique fonctionnelle n'est modifiée.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
