from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"

REQUIRED = "def focus_model("
MARKER = "ASSOCIATION_MAQUETTAGE_GABARIT_V1"

OLD_SIG = '        categories: list[dict[str, Any]],\n        on_create_category: Callable[\n'
NEW_SIG = '        categories: list[dict[str, Any]],\n        page_types: list[dict[str, Any]],\n        default_page_type: str,\n        on_create_category: Callable[\n'
OLD_INIT = '        self._categories: dict[str, dict[str, Any]] = {}\n\n        self.title("Enregistrer comme gabarit du projet")\n        self.geometry("560x430")\n'
NEW_INIT = '        self._categories: dict[str, dict[str, Any]] = {}\n        self._page_types = [\n            dict(item)\n            for item in page_types\n            if isinstance(item, dict)\n            and str(item.get("type", "")).strip()\n        ]\n        self._page_type_labels: dict[str, str] = {\n            str(item.get("type", "")).strip(): str(\n                item.get("title")\n                or item.get("short")\n                or item.get("type")\n                or ""\n            ).strip()\n            for item in self._page_types\n        }\n        self._page_type_var = tk.StringVar(value="Aucune association")\n        normalized_default = str(default_page_type or "").strip()\n        if normalized_default in self._page_type_labels:\n            self._page_type_var.set(\n                self._page_type_labels[normalized_default]\n            )\n\n        self.title("Enregistrer comme gabarit du projet")\n        self.geometry("560x485")\n'
OLD_BUILD = '        self._label(form, "Description facultative", row=4)\n        ctk.CTkEntry(\n            form,\n            textvariable=self._description_var,\n            height=31,\n            border_color=Colors.BORDER,\n            font=Fonts.NORMAL,\n        ).grid(\n            row=5,\n            column=0,\n            columnspan=4,\n            sticky="ew",\n            padx=12,\n            pady=(2, 7),\n        )\n\n        self._label(form, "Note de version en cas de mise à jour", row=6)\n'
NEW_BUILD = '        self._label(form, "Type de page Maquettage associé", row=4)\n\n        page_type_values = [\n            "Aucune association",\n            *[\n                self._page_type_labels[\n                    str(item.get("type", "")).strip()\n                ]\n                for item in self._page_types\n            ],\n        ]\n\n        ctk.CTkOptionMenu(\n            form,\n            values=page_type_values,\n            variable=self._page_type_var,\n            height=31,\n            fg_color=Colors.BUTTON,\n            button_color="#75B6DB",\n            button_hover_color="#619FC3",\n            text_color=Colors.TEXT,\n            font=Fonts.SMALL,\n            dropdown_font=Fonts.SMALL,\n        ).grid(\n            row=5,\n            column=0,\n            columnspan=4,\n            sticky="ew",\n            padx=12,\n            pady=(2, 7),\n        )\n\n        self._label(form, "Description facultative", row=6)\n        ctk.CTkEntry(\n            form,\n            textvariable=self._description_var,\n            height=31,\n            border_color=Colors.BORDER,\n            font=Fonts.NORMAL,\n        ).grid(\n            row=7,\n            column=0,\n            columnspan=4,\n            sticky="ew",\n            padx=12,\n            pady=(2, 7),\n        )\n\n        self._label(form, "Note de version en cas de mise à jour", row=8)\n'
OLD_VERSION_GRID = '        ctk.CTkEntry(\n            form,\n            textvariable=self._version_note_var,\n            height=31,\n            border_color=Colors.BORDER,\n            font=Fonts.NORMAL,\n        ).grid(\n            row=7,\n'
NEW_VERSION_GRID = '        ctk.CTkEntry(\n            form,\n            textvariable=self._version_note_var,\n            height=31,\n            border_color=Colors.BORDER,\n            font=Fonts.NORMAL,\n        ).grid(\n            row=9,\n'
OLD_PAYLOAD = '        payload = {\n            "name": name,\n            "category": "" if category == NO_CATEGORY_LABEL else category,\n            "description": self._description_var.get().strip(),\n            "version_note": self._version_note_var.get().strip(),\n        }\n'
NEW_PAYLOAD = '        selected_label = self._page_type_var.get().strip()\n        mockup_type = ""\n        if selected_label != "Aucune association":\n            for type_id, label in self._page_type_labels.items():\n                if label == selected_label:\n                    mockup_type = type_id\n                    break\n\n        payload = {\n            "name": name,\n            "category": "" if category == NO_CATEGORY_LABEL else category,\n            "description": self._description_var.get().strip(),\n            "version_note": self._version_note_var.get().strip(),\n            "mockup_type": mockup_type,\n        }\n'
ANCHOR = '    @property\n    def _reusable_library_folder(self) -> Path:\n        return Path(__file__).resolve().parents[3] / "bibliotheque_modeles"\n\n'
HELPERS = '    @property\n    def _reusable_library_folder(self) -> Path:\n        return Path(__file__).resolve().parents[3] / "bibliotheque_modeles"\n\n    @property\n    def _mockup_associations_file(self) -> Path:\n        # ASSOCIATION_MAQUETTAGE_GABARIT_V1\n        return Path(self.project.models_folder) / "maquettage_associations.json"\n\n    def _load_mockup_page_types(self) -> list[dict[str, Any]]:\n        configured = getattr(self.project, "mockup_file", None)\n        if configured is not None:\n            path = Path(configured)\n        else:\n            root = getattr(self.project, "root", None)\n            if root is None:\n                return []\n            path = Path(root) / "maquettage" / "premaquette.json"\n\n        if not path.is_file():\n            return []\n\n        try:\n            with path.open("r", encoding="utf-8") as file:\n                data = json.load(file)\n        except (OSError, json.JSONDecodeError):\n            return []\n\n        raw = data.get("page_types", []) if isinstance(data, dict) else []\n        return [\n            dict(item)\n            for item in raw\n            if isinstance(item, dict)\n            and str(item.get("type", "")).strip()\n        ]\n\n    def _load_mockup_associations(self) -> dict[str, str]:\n        path = self._mockup_associations_file\n        if not path.is_file():\n            return {}\n        try:\n            with path.open("r", encoding="utf-8") as file:\n                data = json.load(file)\n        except (OSError, json.JSONDecodeError):\n            return {}\n\n        mapping = data.get("associations", {}) if isinstance(data, dict) else {}\n        if not isinstance(mapping, dict):\n            return {}\n\n        return {\n            str(page_type): str(model_id)\n            for page_type, model_id in mapping.items()\n            if str(page_type).strip() and str(model_id).strip()\n        }\n\n    def _associated_mockup_type_for_model(\n        self,\n        model_identifier: str,\n    ) -> str:\n        identifier = str(model_identifier or "").strip()\n        if not identifier:\n            return ""\n\n        for page_type, model_id in self._load_mockup_associations().items():\n            if model_id == identifier:\n                return page_type\n        return ""\n\n    def _save_mockup_association(\n        self,\n        page_type: str,\n        model_identifier: str,\n    ) -> None:\n        selected_type = str(page_type or "").strip()\n        identifier = str(model_identifier or "").strip()\n\n        associations = self._load_mockup_associations()\n\n        associations = {\n            existing_type: existing_model\n            for existing_type, existing_model in associations.items()\n            if existing_model != identifier\n        }\n\n        if selected_type and identifier:\n            associations[selected_type] = identifier\n\n        path = self._mockup_associations_file\n        path.parent.mkdir(parents=True, exist_ok=True)\n        payload = {\n            "version": "1.0",\n            "mis_a_jour_le": datetime.now().isoformat(),\n            "associations": associations,\n        }\n        with path.open("w", encoding="utf-8") as file:\n            json.dump(\n                payload,\n                file,\n                indent=4,\n                ensure_ascii=False,\n            )\n\n'
OLD_DIALOG_CALL = '        SaveProjectModelDialog(\n            self.parent,\n            default_name=default_name,\n            default_category=self._working_category,\n            categories=self._category_store.load(),\n            on_create_category=lambda created, closed: self._new_category(created, closed),\n            on_validate=self._save_model_payload,\n        )\n'
NEW_DIALOG_CALL = '        SaveProjectModelDialog(\n            self.parent,\n            default_name=default_name,\n            default_category=self._working_category,\n            categories=self._category_store.load(),\n            page_types=self._load_mockup_page_types(),\n            default_page_type=self._associated_mockup_type_for_model(\n                self._working_model_id\n            ),\n            on_create_category=lambda created, closed: self._new_category(created, closed),\n            on_validate=self._save_model_payload,\n        )\n'
OLD_SAVE_TAIL = '        self._working_category = model.category\n        self._working_model_id = model.identifier\n        self._project_models = self._load_project_models()\n        self._model_count_var.set(self._count_label(len(self._project_models)))\n        self._status_var.set(f"Gabarit enregistré : {model.name} ({model.version_label})")\n'
NEW_SAVE_TAIL = '        self._working_category = model.category\n        self._working_model_id = model.identifier\n        self._save_mockup_association(\n            str(payload.get("mockup_type", "")),\n            model.identifier,\n        )\n        self._project_models = self._load_project_models()\n        self._model_count_var.set(self._count_label(len(self._project_models)))\n        self._status_var.set(f"Gabarit enregistré : {model.name} ({model.version_label})")\n'


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        fail(f"bloc introuvable : {label}")
    return source.replace(old, new, 1)


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    source = TARGET.read_text(encoding="utf-8")

    if MARKER in source:
        print("ASSOCIATION_MAQUETTAGE_GABARIT_V1_DEJA_APPLIQUEE")
        return

    if REQUIRED not in source:
        fail("le ciblage Atelier précédent n'est pas détecté")

    source = replace_once(source, OLD_SIG, NEW_SIG, "signature du dialogue")
    source = replace_once(source, OLD_INIT, NEW_INIT, "initialisation du dialogue")
    source = replace_once(source, OLD_BUILD, NEW_BUILD, "formulaire du dialogue")
    source = replace_once(source, OLD_VERSION_GRID, NEW_VERSION_GRID, "note de version")
    source = replace_once(source, OLD_PAYLOAD, NEW_PAYLOAD, "payload d'enregistrement")
    source = replace_once(source, ANCHOR, HELPERS, "helpers Atelier")
    source = replace_once(source, OLD_DIALOG_CALL, NEW_DIALOG_CALL, "appel du dialogue")
    source = replace_once(source, OLD_SAVE_TAIL, NEW_SAVE_TAIL, "sauvegarde de l'association")

    try:
        compile(source, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"model_workshop_view_avant_association_{stamp}.py"
    temp = TARGET.with_suffix(".association_maquettage.tmp")

    try:
        temp.write_text(source, encoding="utf-8")
        py_compile.compile(str(temp), doraise=True)

        shutil.copy2(TARGET, backup)
        temp.replace(TARGET)

        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass

        if backup.exists():
            shutil.copy2(backup, TARGET)

        fail(f"installation annulée automatiquement : {exc}")

    print("ASSOCIATION_MAQUETTAGE_GABARIT_V1_OK")
    print("Le dialogue Enregistrer propose maintenant le type de page Maquettage associé.")
    print("La liaison est enregistrée dans models/maquettage_associations.json.")
    print("Un type possède un gabarit de référence courant.")
    print("Le Centre pourra maintenant identifier avec certitude le gabarit d'une page.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
