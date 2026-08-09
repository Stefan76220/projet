from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
WORKSHOP = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"
DOCUMENT = PROJECT / "src" / "gui" / "views" / "document_view.py"

MARKER_WORKSHOP = "APERCU_REEL_GABARIT_ATELIER_V1"
MARKER_CENTRE = "APERCU_REEL_GABARIT_CENTRE_V1"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def patch_workshop(source: str) -> str:
    if MARKER_WORKSHOP in source:
        return source

    save_anchor = (
        '        self._status_var.set('
        'f"Gabarit enregistré : {model.name} ({model.version_label})")\n'
    )
    if save_anchor not in source:
        fail("point d'enregistrement du gabarit introuvable dans Atelier")

    save_insert = save_anchor + (
        "\n"
        "        # APERCU_REEL_GABARIT_ATELIER_V1\n"
        "        self.parent.after(\n"
        "            160,\n"
        "            lambda current_model=model: self._save_model_centre_preview(\n"
        "                current_model\n"
        "            ),\n"
        "        )\n"
    )
    source = source.replace(save_anchor, save_insert, 1)

    method_anchor = "    def _open_transfer(self) -> None:\n"
    if method_anchor not in source:
        fail("méthode _open_transfer introuvable dans Atelier")

    method = """    def _save_model_centre_preview(self, model: Model) -> None:
        \\"\\"\\"Crée une miniature fidèle de la page actuellement affichée.\\"\\"\\"
        if model.root is None or self._page_editor is None:
            return

        workspace = getattr(self._page_editor, "workspace", None)
        if workspace is None:
            return

        try:
            from PIL import Image, ImageGrab
        except Exception:
            return

        try:
            if not workspace.winfo_exists():
                return

            workspace.update_idletasks()
            try:
                workspace.redraw()
                workspace.update_idletasks()
            except Exception:
                pass

            x1 = int(workspace.winfo_rootx())
            y1 = int(workspace.winfo_rooty())
            width = int(workspace.winfo_width())
            height = int(workspace.winfo_height())

            if width < 40 or height < 40:
                return

            image = ImageGrab.grab(
                bbox=(x1, y1, x1 + width, y1 + height),
                all_screens=True,
            ).convert("RGB")

            w, h = image.size
            pixels = image.load()

            samples = [
                pixels[2, 2],
                pixels[max(2, w - 3), 2],
                pixels[2, max(2, h - 3)],
                pixels[max(2, w - 3), max(2, h - 3)],
            ]
            background = tuple(
                sorted(sample[channel] for sample in samples)[2]
                for channel in range(3)
            )

            def different(pixel) -> bool:
                return (
                    abs(pixel[0] - background[0])
                    + abs(pixel[1] - background[1])
                    + abs(pixel[2] - background[2])
                ) >= 34

            step_y = max(1, h // 180)
            step_x = max(1, w // 180)
            sampled_rows = list(range(0, h, step_y))
            sampled_cols = list(range(0, w, step_x))

            useful_x = []
            for px in sampled_cols:
                changed = sum(
                    1 for py in sampled_rows if different(pixels[px, py])
                )
                if changed >= max(4, int(len(sampled_rows) * 0.22)):
                    useful_x.append(px)

            useful_y = []
            for py in sampled_rows:
                changed = sum(
                    1 for px in sampled_cols if different(pixels[px, py])
                )
                if changed >= max(4, int(len(sampled_cols) * 0.22)):
                    useful_y.append(py)

            if useful_x and useful_y:
                left = max(0, min(useful_x) - 4)
                right = min(w, max(useful_x) + step_x + 4)
                top = max(0, min(useful_y) - 4)
                bottom = min(h, max(useful_y) + step_y + 4)

                if (
                    right - left >= max(40, int(w * 0.20))
                    and bottom - top >= max(40, int(h * 0.30))
                ):
                    image = image.crop((left, top, right, bottom))

            image.thumbnail((600, 850), Image.Resampling.LANCZOS)
            target = Path(model.root) / "apercu_centre.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target, format="PNG", optimize=True)

        except Exception:
            return

"""
    source = source.replace(method_anchor, method + method_anchor, 1)

    use_old = (
        "        self._display_working_page(on_ready=on_ready)\n\n"
        "    def _save_as_project_model(self) -> None:\n"
    )
    use_new = (
        '        if source == "gabarits":\n'
        "            def atelier_ready() -> None:\n"
        "                self.parent.after(\n"
        "                    120,\n"
        "                    lambda current_model=model: self._save_model_centre_preview(\n"
        "                        current_model\n"
        "                    ),\n"
        "                )\n"
        "                on_ready()\n\n"
        "            self._display_working_page(on_ready=atelier_ready)\n"
        "        else:\n"
        "            self._display_working_page(on_ready=on_ready)\n\n"
        "    def _save_as_project_model(self) -> None:\n"
    )
    if use_old not in source:
        fail("fin de _use_model introuvable dans Atelier")
    source = source.replace(use_old, use_new, 1)

    return source


def patch_document(source: str) -> str:
    if MARKER_CENTRE in source:
        return source

    signature = "        def thumbnail_path_for_item(item: dict) -> Path | None:\n"
    if signature not in source:
        fail("fonction thumbnail_path_for_item introuvable dans le Centre")

    addition = """            # APERCU_REEL_GABARIT_CENTRE_V1
            model_id = self._associated_model_id_for_synoptic_item(item)
            if model_id:
                models_folder = Path(self.project.models_folder)

                for summary in list(getattr(self.project, "models", [])):
                    if not isinstance(summary, dict):
                        continue
                    if str(summary.get("identifiant", "")) != model_id:
                        continue

                    folder_name = str(summary.get("dossier", "")).strip()
                    if folder_name:
                        preview = models_folder / folder_name / "apercu_centre.png"
                        if preview.is_file():
                            return preview

                try:
                    for model_file in models_folder.glob("*/modele.json"):
                        if model_file.parent.name.startswith("_"):
                            continue
                        try:
                            raw = model_file.read_text(encoding="utf-8")
                        except OSError:
                            continue
                        if model_id not in raw:
                            continue

                        preview = model_file.parent / "apercu_centre.png"
                        if preview.is_file():
                            return preview
                except OSError:
                    pass

"""
    return source.replace(signature, signature + addition, 1)


def main() -> None:
    if not WORKSHOP.is_file():
        fail(f"fichier introuvable : {WORKSHOP}")
    if not DOCUMENT.is_file():
        fail(f"fichier introuvable : {DOCUMENT}")

    workshop_source = WORKSHOP.read_text(encoding="utf-8")
    document_source = DOCUMENT.read_text(encoding="utf-8")

    workshop_new = patch_workshop(workshop_source)
    document_new = patch_document(document_source)

    try:
        compile(workshop_new, str(WORKSHOP), "exec")
        compile(document_new, str(DOCUMENT), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_workshop = backup_dir / f"model_workshop_view_avant_apercu_reel_{stamp}.py"
    backup_document = backup_dir / f"document_view_avant_apercu_reel_{stamp}.py"

    temp_workshop = WORKSHOP.with_suffix(".apercu_reel.tmp")
    temp_document = DOCUMENT.with_suffix(".apercu_reel.tmp")

    try:
        temp_workshop.write_text(workshop_new, encoding="utf-8")
        temp_document.write_text(document_new, encoding="utf-8")

        py_compile.compile(str(temp_workshop), doraise=True)
        py_compile.compile(str(temp_document), doraise=True)

        shutil.copy2(WORKSHOP, backup_workshop)
        shutil.copy2(DOCUMENT, backup_document)

        temp_workshop.replace(WORKSHOP)
        temp_document.replace(DOCUMENT)

        py_compile.compile(str(WORKSHOP), doraise=True)
        py_compile.compile(str(DOCUMENT), doraise=True)

    except Exception as exc:
        try:
            temp_workshop.unlink(missing_ok=True)
            temp_document.unlink(missing_ok=True)
        except Exception:
            pass

        if backup_workshop.exists():
            shutil.copy2(backup_workshop, WORKSHOP)
        if backup_document.exists():
            shutil.copy2(backup_document, DOCUMENT)

        fail(f"installation annulée automatiquement : {exc}")

    print("APERCU_REEL_GABARIT_V1_OK")
    print("Le Centre utilisera l'aperçu réel du gabarit lorsqu'il existe.")
    print("L'ancienne miniature reste en secours.")
    print(f"Sauvegarde Atelier : {backup_workshop}")
    print(f"Sauvegarde Centre : {backup_document}")


if __name__ == "__main__":
    main()
