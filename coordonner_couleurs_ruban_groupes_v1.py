from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
REQUIRED_MARKER = "PLAN_GROUPES_DYNAMIQUES_V1"
NEW_MARKER = "RUBAN_COULEURS_GROUPES_V1"
BLOCKS = {'_create_group_block': '    def _create_group_block(\n        self,\n        parent,\n        group_definition: dict[str, Any],\n        width: int,\n    ) -> ctk.CTkFrame:\n        """Crée un groupe dont toute la palette dérive de sa couleur."""\n        group_id = str(group_definition.get("id", ""))\n        title = str(group_definition.get("title", "Groupe"))\n        symbol = str(group_definition.get("symbol", "▦"))\n        accent = str(group_definition.get("accent", self.INK))\n        protected = bool(group_definition.get("protected", False))\n\n        group_soft = self._mix_color_with_white(accent, 0.90)\n        group_title_soft = self._mix_color_with_white(accent, 0.84)\n\n        block = ctk.CTkFrame(\n            parent,\n            width=width,\n            height=104,\n            fg_color=group_soft,\n            corner_radius=5,\n            border_width=1,\n            border_color=group_title_soft,\n        )\n        block.pack_propagate(False)\n        block.grid_propagate(False)\n        block.grid_columnconfigure(0, weight=1)\n        block.grid_rowconfigure(0, weight=1)\n\n        definitions = [\n            definition\n            for definition in self._page_types()\n            if str(definition.get("group", "")) == group_id\n        ]\n        type_columns = max(1, (len(definitions) + 1) // 2)\n\n        types_frame = ctk.CTkFrame(block, fg_color="transparent")\n        types_frame.grid(\n            row=0,\n            column=0,\n            sticky="nsew",\n            padx=3,\n            pady=(2, 1),\n        )\n        for column in range(type_columns):\n            types_frame.grid_columnconfigure(column, weight=0)\n        for row in range(2):\n            types_frame.grid_rowconfigure(row, weight=1)\n\n        if definitions:\n            for index, definition in enumerate(definitions):\n                column = index // 2\n                row = index % 2\n                button = self._create_page_type_button(types_frame, definition)\n                button.grid(\n                    row=row,\n                    column=column,\n                    sticky="nsew",\n                    padx=1,\n                    pady=1,\n                )\n        else:\n            ctk.CTkLabel(\n                types_frame,\n                text="Aucun type",\n                font=(Fonts.FAMILY, 9),\n                text_color=self.TEXT_LIGHT,\n            ).grid(row=0, column=0, rowspan=2, padx=8, pady=10)\n\n        title_bar = ctk.CTkFrame(\n            block,\n            height=18,\n            fg_color=group_title_soft,\n            corner_radius=0,\n        )\n        title_bar.grid(row=1, column=0, sticky="ew", padx=1, pady=(0, 1))\n        title_bar.grid_propagate(False)\n        title_bar.grid_columnconfigure(0, weight=1)\n\n        title_label = ctk.CTkLabel(\n            title_bar,\n            text=f"{symbol}  {title}",\n            font=(Fonts.FAMILY, 9, "bold"),\n            text_color=accent,\n            anchor="center",\n        )\n        title_label.grid(row=0, column=0, sticky="nsew", padx=3)\n\n        if not protected:\n            self._bind_custom_group_drag(title_bar, title_label, group_id)\n\n        return block', '_create_page_type_button': '    def _create_page_type_button(\n        self,\n        parent,\n        definition: dict[str, Any],\n    ) -> ctk.CTkButton:\n        page_type = str(definition.get("type", ""))\n        full_title = str(definition.get("title", "Page"))\n        short_title = str(definition.get("short", full_title))\n        symbol = str(definition.get("symbol", "?"))\n        group_id = str(definition.get("group", "pages_interieures"))\n        group = self._group_for(group_id)\n        group_accent = str(group.get("accent", self.INK))\n\n        # Chaque type garde sa personnalité par son symbole et son libellé,\n        # mais sa couleur appartient clairement à son groupe.\n        definitions = [\n            item\n            for item in self._page_types()\n            if str(item.get("group", "")) == group_id\n        ]\n        try:\n            position = next(\n                index\n                for index, item in enumerate(definitions)\n                if str(item.get("type", "")) == page_type\n            )\n        except StopIteration:\n            position = 0\n\n        tone_factors = (0.84, 0.79, 0.74, 0.87)\n        factor = tone_factors[position % len(tone_factors)]\n        button_color = self._mix_color_with_white(group_accent, factor)\n        hover_color = self._mix_color_with_white(\n            group_accent,\n            max(0.58, factor - 0.14),\n        )\n        border_color = self._mix_color_with_white(group_accent, 0.60)\n\n        button = ctk.CTkButton(\n            parent,\n            text=f"{symbol}\\n{short_title}",\n            width=66,\n            height=39,\n            corner_radius=5,\n            fg_color=button_color,\n            hover_color=hover_color,\n            text_color=group_accent,\n            border_width=1,\n            border_color=border_color,\n            font=(Fonts.FAMILY, 9),\n            command=lambda selected=definition: self._add_item(selected),\n        )\n        self._attach_tooltip(button, full_title)\n        if page_type:\n            self._page_type_buttons[page_type] = button\n        return button\n\n    @staticmethod\n    def _mix_color_with_white(color: str, white_ratio: float) -> str:\n        """Éclaircit une couleur sans changer sa famille chromatique."""\n        value = str(color).lstrip("#")\n        if len(value) != 6:\n            return color\n        try:\n            red = int(value[0:2], 16)\n            green = int(value[2:4], 16)\n            blue = int(value[4:6], 16)\n        except ValueError:\n            return color\n\n        ratio = max(0.0, min(1.0, float(white_ratio)))\n        red = int(red + (255 - red) * ratio)\n        green = int(green + (255 - green) * ratio)\n        blue = int(blue + (255 - blue) * ratio)\n        return f"#{red:02X}{green:02X}{blue:02X}"'}
METHODS = ['_create_group_block', '_create_page_type_button']


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
        line = lines[index]
        if line.startswith("    def ") or line.startswith("    @"):
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
        print("RUBAN_COULEURS_GROUPES_DEJA_APPLIQUE")
        return

    if REQUIRED_MARKER not in original:
        fail(
            "la version Plan du livre / groupes dynamiques attendue "
            "n'est pas détectée. Par sécurité, la correction est refusée."
        )

    candidate = original
    for name in METHODS:
        candidate = replace_method(candidate, name, BLOCKS[name])

    candidate = candidate.replace(
        "# PLAN_GROUPES_DYNAMIQUES_V1",
        "# PLAN_GROUPES_DYNAMIQUES_V1\n        # RUBAN_COULEURS_GROUPES_V1",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_couleurs_ruban_{stamp}.py"
    temporary = TARGET.with_suffix(".couleurs_ruban.tmp")

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

    print("RUBAN_COULEURS_GROUPES_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Chaque groupe possède maintenant une famille de couleurs cohérente.")
    print("Les types de pages utilisent des nuances de la couleur de leur groupe.")
    print("Les nouveaux groupes et leurs futurs types suivent automatiquement la même règle.")
    print("Aucune logique du Plan du livre n'a été modifiée.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
