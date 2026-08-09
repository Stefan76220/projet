from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
BACKGROUND = PROJECT / "assets" / "interface" / "backgrounds" / "editorial_bg_soft.png"

REQUIRED_MARKER = "FOND_DISCRET_MAQUETTAGE_V1"
NEW_MARKER = "FOND_DISCRET_PLAN_LIVRE_V1"

HELPERS = '    def _install_plan_background(self) -> None:\n        """Pose le décor léger dans l\'espace libre du Plan du livre."""\n        self._plan_background_label = None\n        self._plan_background_source = None\n        self._plan_background_photo = None\n\n        if self._sequence_frame is None:\n            return\n\n        background_path = (\n            Path(__file__).resolve().parents[3]\n            / "assets"\n            / "interface"\n            / "backgrounds"\n            / "editorial_bg_soft.png"\n        )\n        if not background_path.is_file():\n            return\n\n        try:\n            from PIL import Image\n\n            self._plan_background_source = Image.open(\n                background_path\n            ).convert("RGB")\n\n            label = tk.Label(\n                self._sequence_frame,\n                image="",\n                text="",\n                borderwidth=0,\n                highlightthickness=0,\n                background=self.RIBBON_BG,\n                takefocus=False,\n            )\n            self._plan_background_label = label\n\n            self._sequence_frame.bind(\n                "<Configure>",\n                self._refresh_plan_background,\n                add="+",\n            )\n            self._sequence_frame.after_idle(\n                self._refresh_plan_background\n            )\n        except Exception:\n            self._plan_background_label = None\n            self._plan_background_source = None\n            self._plan_background_photo = None\n\n    def _refresh_plan_background(self, _event=None) -> None:\n        """Adapte le décor à la place réellement libre à droite des cartes."""\n        frame = self._sequence_frame\n        label = getattr(self, "_plan_background_label", None)\n        source = getattr(self, "_plan_background_source", None)\n        if frame is None or label is None or source is None:\n            return\n\n        try:\n            from PIL import Image, ImageTk\n\n            frame_width = max(1, int(frame.winfo_width()))\n            frame_height = max(1, int(frame.winfo_height()))\n\n            available_width = frame_width - 860\n            if available_width < 150 or frame_height < 120:\n                label.place_forget()\n                return\n\n            target_width = min(500, max(150, available_width - 22))\n            target_height = min(max(180, frame_height - 24), 620)\n\n            source_ratio = source.width / source.height\n            target_ratio = target_width / target_height\n\n            if target_ratio > source_ratio:\n                resize_width = target_width\n                resize_height = max(\n                    target_height,\n                    int(round(target_width / source_ratio)),\n                )\n            else:\n                resize_height = target_height\n                resize_width = max(\n                    target_width,\n                    int(round(target_height * source_ratio)),\n                )\n\n            resized = source.resize(\n                (resize_width, resize_height),\n                Image.Resampling.LANCZOS,\n            )\n\n            left = max(0, (resize_width - target_width) // 2)\n            top = max(0, (resize_height - target_height) // 2)\n            cropped = resized.crop(\n                (\n                    left,\n                    top,\n                    left + target_width,\n                    top + target_height,\n                )\n            )\n\n            photo = ImageTk.PhotoImage(cropped)\n            self._plan_background_photo = photo\n            label.configure(image=photo)\n\n            x = max(0, frame_width - target_width - 18)\n            y = 10\n            label.place(\n                x=x,\n                y=y,\n                width=target_width,\n                height=target_height,\n            )\n            label.lift()\n        except Exception:\n            try:\n                label.place_forget()\n            except Exception:\n                pass\n\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    if not BACKGROUND.is_file():
        fail(f"fond discret introuvable : {BACKGROUND}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("FOND_DISCRET_PLAN_LIVRE_DEJA_APPLIQUE")
        return

    if REQUIRED_MARKER not in original:
        fail(
            "le fond discret du Bureau de maquettage n'est pas détecté. "
            "Par sécurité, aucune modification n'est appliquée."
        )

    candidate = original

    anchor = "    def _refresh_sequence(self) -> None:\n"
    if anchor not in candidate:
        fail("point d'insertion du décor du Plan du livre introuvable")
    candidate = candidate.replace(
        anchor,
        HELPERS + anchor,
        1,
    )

    anchor2 = "        self._sequence_frame.grid_columnconfigure(0, weight=1)\n"
    if anchor2 not in candidate:
        fail("zone du Plan du livre introuvable")
    candidate = candidate.replace(
        anchor2,
        anchor2
        + "\n"
        + "        # FOND_DISCRET_PLAN_LIVRE_V1\n"
        + "        self._install_plan_background()\n",
        1,
    )

    anchor3 = (
        "        self._update_page_type_button_states()\n"
        "        self._update_selection_controls()\n"
    )
    if anchor3 not in candidate:
        fail("fin du rafraîchissement du Plan du livre introuvable")
    candidate = candidate.replace(
        anchor3,
        anchor3 + "        self._refresh_plan_background()\n",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_fond_plan_{stamp}.py"
    temporary = TARGET.with_suffix(".fond_plan.tmp")

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

    print("FOND_DISCRET_PLAN_LIVRE_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Fond utilisé : assets/interface/backgrounds/editorial_bg_soft.png")
    print("Le décor est maintenant visible dans l'espace libre du Plan du livre.")
    print("Les cartes, le panneau contextuel, le ruban et la logique de déplacement sont inchangés.")
    print("Sur une fenêtre trop étroite, le décor se masque automatiquement.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
