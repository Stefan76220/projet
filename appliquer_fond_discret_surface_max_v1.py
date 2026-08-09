from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
BACKGROUND = (
    PROJECT
    / "assets"
    / "interface"
    / "backgrounds"
    / "editorial_bg_soft.png"
)

REQUIRED_MARKERS = (
    "FOND_DISCRET_MAQUETTAGE_V1",
    "FOND_DISCRET_PLAN_LIVRE_V1",
    "RUBAN_PAINT_SANS_MINIATURES_V1",
)
NEW_MARKER = "FOND_DISCRET_SURFACE_MAX_V1"

NEW_PLAN_REFRESH = '    def _refresh_plan_background(self, _event=None) -> None:\n        """Étend le décor léger sur toute la surface visible du Plan du livre."""\n        frame = self._sequence_frame\n        label = getattr(self, "_plan_background_label", None)\n        source = getattr(self, "_plan_background_source", None)\n        if frame is None or label is None or source is None:\n            return\n\n        try:\n            from PIL import Image, ImageTk\n\n            width = max(1, int(frame.winfo_width()))\n            height = max(1, int(frame.winfo_height()))\n            if width <= 2 or height <= 2:\n                return\n\n            source_ratio = source.width / source.height\n            target_ratio = width / height\n\n            if target_ratio > source_ratio:\n                resize_width = width\n                resize_height = max(\n                    height,\n                    int(round(width / source_ratio)),\n                )\n            else:\n                resize_height = height\n                resize_width = max(\n                    width,\n                    int(round(height * source_ratio)),\n                )\n\n            resized = source.resize(\n                (resize_width, resize_height),\n                Image.Resampling.LANCZOS,\n            )\n\n            left = max(0, (resize_width - width) // 2)\n            top = max(0, (resize_height - height) // 2)\n            cropped = resized.crop(\n                (left, top, left + width, top + height)\n            )\n\n            photo = ImageTk.PhotoImage(cropped)\n            self._plan_background_photo = photo\n            label.configure(image=photo)\n            label.place(\n                x=0,\n                y=0,\n                width=width,\n                height=height,\n            )\n            # Le décor est un vrai arrière-plan : les cartes restent devant.\n            label.lower()\n        except Exception:\n            try:\n                label.place_forget()\n            except Exception:\n                pass'
RIBBON_HELPERS = '    def _install_ribbon_background(self, ribbon) -> None:\n        """Pose le même fond léger derrière toute la surface du ruban."""\n        background_path = (\n            Path(__file__).resolve().parents[3]\n            / "assets"\n            / "interface"\n            / "backgrounds"\n            / "editorial_bg_soft.png"\n        )\n        if not background_path.is_file():\n            return\n\n        try:\n            from PIL import Image, ImageTk\n\n            source = Image.open(background_path).convert("RGB")\n            label = tk.Label(\n                ribbon,\n                image="",\n                text="",\n                borderwidth=0,\n                highlightthickness=0,\n                background=self.RIBBON_BG,\n                takefocus=False,\n            )\n            label.place(x=0, y=0, relwidth=1, relheight=1)\n            label.lower()\n\n            # Références conservées pour éviter la libération des images Tk.\n            ribbon._soft_background_source = source\n            ribbon._soft_background_label = label\n            ribbon._soft_background_photo = None\n\n            def redraw(_event=None) -> None:\n                try:\n                    width = max(1, int(ribbon.winfo_width()))\n                    height = max(1, int(ribbon.winfo_height()))\n                    if width <= 2 or height <= 2:\n                        return\n\n                    source_ratio = source.width / source.height\n                    target_ratio = width / height\n\n                    if target_ratio > source_ratio:\n                        resize_width = width\n                        resize_height = max(\n                            height,\n                            int(round(width / source_ratio)),\n                        )\n                    else:\n                        resize_height = height\n                        resize_width = max(\n                            width,\n                            int(round(height * source_ratio)),\n                        )\n\n                    resized = source.resize(\n                        (resize_width, resize_height),\n                        Image.Resampling.LANCZOS,\n                    )\n                    left = max(0, (resize_width - width) // 2)\n                    top = max(0, (resize_height - height) // 2)\n                    cropped = resized.crop(\n                        (left, top, left + width, top + height)\n                    )\n\n                    photo = ImageTk.PhotoImage(cropped)\n                    ribbon._soft_background_photo = photo\n                    label.configure(image=photo)\n                    label.place(\n                        x=0,\n                        y=0,\n                        width=width,\n                        height=height,\n                    )\n                    label.lower()\n                except Exception:\n                    pass\n\n            ribbon.bind("<Configure>", redraw, add="+")\n            ribbon.after_idle(redraw)\n        except Exception:\n            pass\n\n'


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

    return (
        "".join(lines[:start])
        + new_block.rstrip()
        + "\n\n"
        + "".join(lines[end:])
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")
    if not BACKGROUND.is_file():
        fail(f"fond discret introuvable : {BACKGROUND}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("FOND_DISCRET_SURFACE_MAX_DEJA_APPLIQUE")
        return

    missing = [marker for marker in REQUIRED_MARKERS if marker not in original]
    if missing:
        fail(
            "la version attendue du Maquettage n'est pas détectée : "
            + ", ".join(missing)
        )

    candidate = original

    # 1. L'ancien décor limité à droite devient un vrai arrière-plan
    #    couvrant toute la zone de cartes.
    candidate = replace_method(
        candidate,
        "_refresh_plan_background",
        NEW_PLAN_REFRESH,
    )

    # 2. Même décor derrière toute la surface du ruban.
    anchor = "    def _create_ribbon(self, parent) -> ctk.CTkFrame:\n"
    if anchor not in candidate:
        fail("méthode _create_ribbon introuvable")
    candidate = candidate.replace(
        anchor,
        RIBBON_HELPERS + anchor,
        1,
    )

    call_anchor = "        ribbon.grid_rowconfigure(0, weight=1)\n"
    if call_anchor not in candidate:
        fail("point d'installation du fond du ruban introuvable")
    candidate = candidate.replace(
        call_anchor,
        call_anchor
        + "\n"
        + "        self._install_ribbon_background(ribbon)\n",
        1,
    )

    # 3. Marque la version sans toucher aux règles fonctionnelles.
    marker_anchor = "        # RUBAN_PAINT_SANS_MINIATURES_V1\n"
    if marker_anchor not in candidate:
        fail("marqueur du ruban Paint introuvable")
    candidate = candidate.replace(
        marker_anchor,
        marker_anchor
        + "        # FOND_DISCRET_SURFACE_MAX_V1\n",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"mockup_view_avant_fond_surface_max_{stamp}.py"
    )
    temporary = TARGET.with_suffix(".fond_surface_max.tmp")

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

    print("FOND_DISCRET_SURFACE_MAX_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Le fond discret couvre maintenant toute la zone du ruban.")
    print("Le fond discret couvre toute la surface visible du Plan du livre.")
    print("Les cartes, groupes colorés et panneaux d'outils restent au premier plan.")
    print("Aucune logique de page, sélection, déplacement ou recto-verso n'est modifiée.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
