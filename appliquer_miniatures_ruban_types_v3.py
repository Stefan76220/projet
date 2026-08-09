from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
RESTORED_BACKUP = (
    PROJECT
    / "cache"
    / "correctifs"
    / "mockup_view_avant_miniatures_ruban_20260807_185147.py"
)
REQUIRED_MARKER = "MINIATURES_REALISTES_V1"
FORBIDDEN_MARKERS = (
    "MINIATURES_RUBAN_TYPES_V1",
    "MINIATURES_RUBAN_TYPES_V2",
)
NEW_MARKER = "MINIATURES_RUBAN_TYPES_V3"

NEW_BUTTON = '    def _create_page_type_button(\n        self,\n        parent,\n        definition: dict[str, Any],\n    ) -> ctk.CTkButton:\n        """Bouton du ruban conservant le CTkButton d\'origine + miniature."""\n        page_type = str(definition.get("type", ""))\n        full_title = str(definition.get("title", "Page"))\n        short_title = str(definition.get("short", full_title))\n        symbol = str(definition.get("symbol", "?"))\n        group_id = str(definition.get("group", "pages_interieures"))\n        group = self._group_for(group_id)\n        group_accent = str(group.get("accent", self.INK))\n\n        definitions = [\n            item\n            for item in self._page_types()\n            if str(item.get("group", "")) == group_id\n        ]\n        try:\n            position = next(\n                index\n                for index, item in enumerate(definitions)\n                if str(item.get("type", "")) == page_type\n            )\n        except StopIteration:\n            position = 0\n\n        tone_factors = (0.84, 0.79, 0.74, 0.87)\n        factor = tone_factors[position % len(tone_factors)]\n        button_color = self._mix_color_with_white(group_accent, factor)\n        hover_color = self._mix_color_with_white(\n            group_accent,\n            max(0.58, factor - 0.14),\n        )\n        border_color = self._mix_color_with_white(group_accent, 0.60)\n\n        photo = self._thumbnail_photo_for_definition(\n            definition,\n            subsample=14,\n        )\n\n        button = ctk.CTkButton(\n            parent,\n            text=short_title if photo is not None else f"{symbol}\\n{short_title}",\n            image=photo,\n            compound="left" if photo is not None else "center",\n            width=72,\n            height=39,\n            corner_radius=5,\n            fg_color=button_color,\n            hover_color=hover_color,\n            text_color=group_accent,\n            border_width=1,\n            border_color=border_color,\n            font=(Fonts.FAMILY, 8 if photo is not None else 9),\n            command=lambda selected=definition: self._add_item(selected),\n        )\n\n        # Garde une référence explicite en plus du cache Tkinter.\n        button._page_thumbnail_ref = photo\n\n        self._attach_tooltip(button, full_title)\n        if page_type:\n            self._page_type_buttons[page_type] = button\n        return button'


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
    if not RESTORED_BACKUP.is_file():
        fail(f"sauvegarde de référence introuvable : {RESTORED_BACKUP}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("MINIATURES_RUBAN_TYPES_V3_DEJA_APPLIQUE")
        return

    if REQUIRED_MARKER not in original:
        fail("les miniatures réalistes du Plan du livre ne sont pas détectées")

    for marker in FORBIDDEN_MARKERS:
        if marker in original:
            fail(
                "un ancien essai du ruban est encore présent. "
                "La version restaurée doit être utilisée."
            )

    # Vérification dynamique : le fichier courant doit être exactement la
    # sauvegarde que l'utilisateur vient de restaurer. Aucun hash inventé.
    current_hash = sha256(TARGET)
    backup_hash = sha256(RESTORED_BACKUP)
    if current_hash != backup_hash:
        fail(
            "mockup_view.py ne correspond pas à la sauvegarde restaurée. "
            f"Actuel={current_hash} ; sauvegarde={backup_hash}"
        )

    candidate = replace_method(
        original,
        "_create_page_type_button",
        NEW_BUTTON,
    )
    candidate = candidate.replace(
        "# MINIATURES_REALISTES_V1",
        "# MINIATURES_REALISTES_V1\n"
        "        # MINIATURES_RUBAN_TYPES_V3",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_miniatures_ruban_v3_{stamp}.py"
    temporary = TARGET.with_suffix(".miniatures_ruban_v3.tmp")

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

    print("MINIATURES_RUBAN_TYPES_V3_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Cette version conserve les CTkButton d'origine.")
    print("Seule une miniature est ajoutée à gauche du nom du type.")
    print("La logique normal/disabled du ruban reste inchangée.")
    print("Les outils de gestion ne sont pas modifiés.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
