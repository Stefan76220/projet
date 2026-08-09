from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
WORKSHOP = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"
DOCUMENT = PROJECT / "src" / "gui" / "views" / "document_view.py"

MARKER_WORKSHOP = "APERCU_REEL_GABARIT_ATELIER_V2"
MARKER_CENTRE = "APERCU_REEL_GABARIT_CENTRE_V2"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def patch_workshop(source: str) -> str:
    if MARKER_WORKSHOP in source:
        return source

    focus_old = '''        if self._working_model_id == identifier:
            self._focus_current_editor()
            return True
'''
    focus_new = '''        if self._working_model_id == identifier:
            self._focus_current_editor()
            # APERCU_REEL_GABARIT_ATELIER_V2
            self.parent.after(
                120,
                self._save_active_model_centre_preview,
            )
            return True
'''
    if focus_old not in source:
        fail("bloc focus_model déjà actif introuvable")
    source = source.replace(focus_old, focus_new, 1)

    use_old = '''        self._use_model(
            target,
            "gabarits",
            on_ready=self._focus_current_editor,
        )
        return True
'''
    use_new = '''        def ready_with_preview() -> None:
            self._focus_current_editor()
            self.parent.after(
                120,
                lambda current_model=target: self._save_model_centre_preview(
                    current_model
                ),
            )

        self._use_model(
            target,
            "gabarits",
            on_ready=ready_with_preview,
        )
        return True
'''
    if use_old not in source:
        fail("appel _use_model de focus_model introuvable")
    source = source.replace(use_old, use_new, 1)

    save_anchor = (
        '        self._status_var.set('
        'f"Gabarit enregistré : {model.name} ({model.version_label})")\n'
    )
    if save_anchor not in source:
        fail("fin de l'enregistrement du gabarit introuvable")

    save_new = save_anchor + '''        self.parent.after(
            160,
            lambda current_model=model: self._save_model_centre_preview(
                current_model
            ),
        )
'''
    source = source.replace(save_anchor, save_new, 1)

    method_anchor = "    def _open_transfer(self) -> None:\n"
    if method_anchor not in source:
        fail("méthode _open_transfer introuvable")

    preview_methods = '''    def _save_active_model_centre_preview(self) -> None:
        identifier = str(self._working_model_id or "").strip()
        if not identifier:
            return

        target = next(
            (
                model
                for model in self._load_project_models()
                if str(model.identifier) == identifier
            ),
            None,
        )
        if target is not None:
            self._save_model_centre_preview(target)

    def _save_model_centre_preview(self, model: Model) -> None:
        # Capture uniquement la zone de travail de l'Atelier afin de fournir
        # au Centre une miniature fidèle du gabarit réellement affiché.
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

            corner_points = (
                (2, 2),
                (max(2, w - 3), 2),
                (2, max(2, h - 3)),
                (max(2, w - 3), max(2, h - 3)),
            )
            samples = [
                pixels[min(w - 1, px), min(h - 1, py)]
                for px, py in corner_points
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

            step_x = max(1, w // 180)
            step_y = max(1, h // 180)
            cols = list(range(0, w, step_x))
            rows = list(range(0, h, step_y))

            useful_x = []
            for px in cols:
                changed = sum(
                    1 for py in rows if different(pixels[px, py])
                )
                if changed >= max(4, int(len(rows) * 0.22)):
                    useful_x.append(px)

            useful_y = []
            for py in rows:
                changed = sum(
                    1 for px in cols if different(pixels[px, py])
                )
                if changed >= max(4, int(len(cols) * 0.22)):
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
            target_path = Path(model.root) / "apercu_centre.png"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(target_path, format="PNG", optimize=True)

        except Exception:
            return

'''
    source = source.replace(
        method_anchor,
        preview_methods + method_anchor,
        1,
    )

    return source


def patch_document(source: str) -> str:
    if MARKER_CENTRE in source:
        return source

    signature = "        def thumbnail_path_for_item(item: dict) -> Path | None:\n"
    if signature not in source:
        fail("fonction thumbnail_path_for_item introuvable dans le Centre")

    addition = '''            # APERCU_REEL_GABARIT_CENTRE_V2
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
                        preview = (
                            models_folder
                            / folder_name
                            / "apercu_centre.png"
                        )
                        if preview.is_file():
                            return preview

                try:
                    for model_file in models_folder.glob("*/modele.json"):
                        if model_file.parent.name.startswith("_"):
                            continue
                        try:
                            with model_file.open("r", encoding="utf-8") as file:
                                raw = json.load(file)
                        except (OSError, json.JSONDecodeError):
                            continue

                        possible_ids = {
                            str(raw.get("identifiant", "")),
                            str(raw.get("identifier", "")),
                            str(raw.get("id", "")),
                        }
                        if model_id not in possible_ids:
                            continue

                        preview = model_file.parent / "apercu_centre.png"
                        if preview.is_file():
                            return preview
                except OSError:
                    pass

'''
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

    backup_workshop = (
        backup_dir / f"model_workshop_view_avant_apercu_reel_v2_{stamp}.py"
    )
    backup_document = (
        backup_dir / f"document_view_avant_apercu_reel_v2_{stamp}.py"
    )

    temp_workshop = WORKSHOP.with_suffix(".apercu_reel_v2.tmp")
    temp_document = DOCUMENT.with_suffix(".apercu_reel_v2.tmp")

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

    print("APERCU_REEL_GABARIT_V2_OK")
    print("Atelier : aperçu réel généré à l'ouverture ou à l'enregistrement.")
    print("Centre : cet aperçu remplace la miniature Maquettage.")
    print("Sans aperçu disponible : l'ancienne miniature reste affichée.")


if __name__ == "__main__":
    main()
