from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
EXPECTED_SHA256 = '36a171f5d6a2fd46e2dc9c1c8b6abba04c1a0d0a4e5c586ca479de02db137bc1'
REQUIRED_MARKER = "MINIATURES_REALISTES_V1"
FORBIDDEN_MARKER = "MINIATURES_RUBAN_TYPES_V1"
NEW_MARKER = "MINIATURES_RUBAN_TYPES_V2"

NEW_BUTTON = '    def _create_page_type_button(\n        self,\n        parent,\n        definition: dict[str, Any],\n    ):\n        """Bouton compact du ruban avec la miniature réelle de la page."""\n        page_type = str(definition.get("type", ""))\n        full_title = str(definition.get("title", "Page"))\n        short_title = str(definition.get("short", full_title))\n        group_id = str(definition.get("group", "pages_interieures"))\n        group = self._group_for(group_id)\n        group_accent = str(group.get("accent", self.INK))\n\n        definitions = [\n            item\n            for item in self._page_types()\n            if str(item.get("group", "")) == group_id\n        ]\n        try:\n            position = next(\n                index\n                for index, item in enumerate(definitions)\n                if str(item.get("type", "")) == page_type\n            )\n        except StopIteration:\n            position = 0\n\n        tone_factors = (0.84, 0.79, 0.74, 0.87)\n        factor = tone_factors[position % len(tone_factors)]\n        button_color = self._mix_color_with_white(group_accent, factor)\n        hover_color = self._mix_color_with_white(\n            group_accent,\n            max(0.58, factor - 0.14),\n        )\n        border_color = self._mix_color_with_white(group_accent, 0.60)\n        disabled_color = self._mix_color_with_white(group_accent, 0.93)\n        disabled_text = self._mix_color_with_white(group_accent, 0.45)\n\n        button = ctk.CTkFrame(\n            parent,\n            width=66,\n            height=39,\n            fg_color=button_color,\n            corner_radius=5,\n            border_width=1,\n            border_color=border_color,\n        )\n        button.grid_propagate(False)\n\n        page_holder = ctk.CTkFrame(\n            button,\n            width=24,\n            height=34,\n            fg_color="#FFFFFF",\n            corner_radius=2,\n            border_width=1,\n            border_color=border_color,\n        )\n        page_holder.place(x=3, y=2)\n\n        image_label = tk.Label(\n            page_holder,\n            image="",\n            text="",\n            background="#FFFFFF",\n            borderwidth=0,\n            highlightthickness=0,\n        )\n        image_label.place(relx=0.5, rely=0.5, anchor="center")\n\n        photo = self._thumbnail_photo_for_definition(\n            definition,\n            subsample=14,\n        )\n        if photo is not None:\n            image_label.configure(image=photo)\n            button._thumbnail_ref = photo\n        else:\n            image_label.configure(\n                text=str(definition.get("symbol", "?")),\n                font=(Fonts.FAMILY, 9, "bold"),\n                foreground=group_accent,\n            )\n\n        text_label = ctk.CTkLabel(\n            button,\n            text=short_title,\n            width=35,\n            height=35,\n            fg_color="transparent",\n            text_color=group_accent,\n            font=(Fonts.FAMILY, 8),\n            anchor="center",\n            justify="center",\n            wraplength=34,\n        )\n        text_label.place(x=29, y=2)\n\n        button._page_enabled = True\n        button._normal_color = button_color\n        button._hover_color = hover_color\n        button._disabled_color = disabled_color\n        button._normal_text_color = group_accent\n        button._disabled_text_color = disabled_text\n        button._text_label_ref = text_label\n\n        def activate(_event=None) -> None:\n            if bool(getattr(button, "_page_enabled", True)):\n                self._add_item(definition)\n\n        def enter(_event=None) -> None:\n            if bool(getattr(button, "_page_enabled", True)):\n                button.configure(fg_color=button._hover_color)\n\n        def leave(_event=None) -> None:\n            if bool(getattr(button, "_page_enabled", True)):\n                button.configure(fg_color=button._normal_color)\n            else:\n                button.configure(fg_color=button._disabled_color)\n\n        for widget in (button, page_holder, image_label, text_label):\n            widget.bind("<Button-1>", activate)\n            widget.bind("<Enter>", enter)\n            widget.bind("<Leave>", leave)\n\n        self._attach_tooltip(button, full_title)\n        if page_type:\n            self._page_type_buttons[page_type] = button\n        return button'
NEW_STATES = '    def _update_page_type_button_states(self) -> None:\n        """Active/désactive les cartes du ruban sans supposer un CTkButton."""\n        present_types = {\n            str(item.get("type", ""))\n            for item in self._items()\n        }\n\n        for page_type, button in self._page_type_buttons.items():\n            definition = self._definition_for(page_type)\n            is_single = bool(definition.get("single", False))\n            state = (\n                "disabled"\n                if is_single and page_type in present_types\n                else "normal"\n            )\n            if self._page_type_button_states.get(page_type) == state:\n                continue\n\n            enabled = state == "normal"\n            button._page_enabled = enabled\n\n            normal_color = getattr(\n                button,\n                "_normal_color",\n                self.GROUP_BG,\n            )\n            disabled_color = getattr(\n                button,\n                "_disabled_color",\n                self.RIBBON_BG,\n            )\n            button.configure(\n                fg_color=normal_color if enabled else disabled_color\n            )\n\n            label = getattr(button, "_text_label_ref", None)\n            if label is not None:\n                label.configure(\n                    text_color=(\n                        getattr(\n                            button,\n                            "_normal_text_color",\n                            self.INK,\n                        )\n                        if enabled\n                        else getattr(\n                            button,\n                            "_disabled_text_color",\n                            self.TEXT_LIGHT,\n                        )\n                    )\n                )\n\n            self._page_type_button_states[page_type] = state'


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

    return (
        "".join(lines[:start])
        + new_block.rstrip()
        + "\n\n"
        + "".join(lines[end:])
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("MINIATURES_RUBAN_TYPES_V2_DEJA_APPLIQUE")
        return

    if FORBIDDEN_MARKER in original:
        fail(
            "l'ancien essai défaillant est encore présent. "
            "La restauration précédente doit être faite avant ce correctif."
        )

    if REQUIRED_MARKER not in original:
        fail("les miniatures réalistes du Plan du livre ne sont pas détectées")

    current_hash = sha256(TARGET)
    if current_hash != EXPECTED_SHA256:
        fail(
            "mockup_view.py n'est pas exactement la version restaurée et validée. "
            f"SHA256 actuel : {current_hash}"
        )

    candidate = replace_method(
        original,
        "_create_page_type_button",
        NEW_BUTTON,
    )
    candidate = replace_method(
        candidate,
        "_update_page_type_button_states",
        NEW_STATES,
    )
    candidate = candidate.replace(
        "# MINIATURES_REALISTES_V1",
        "# MINIATURES_REALISTES_V1\n"
        "        # MINIATURES_RUBAN_TYPES_V2",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_miniatures_ruban_v2_{stamp}.py"
    temporary = TARGET.with_suffix(".miniatures_ruban_v2.tmp")

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

    print("MINIATURES_RUBAN_TYPES_V2_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Correction : le ruban conserve désormais ses widgets compatibles avec la gestion des états.")
    print("Miniature à gauche + nom court à droite, sans agrandir les groupes.")
    print("Les outils de gestion ne sont pas modifiés.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
