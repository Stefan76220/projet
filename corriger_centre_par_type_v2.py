from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import shutil

TARGET = Path("src/gui/views/document_view.py")


PROJECT_METHOD = '''    def _project_type_key(self) -> str:\n        return str(\n            getattr(\n                self.project,\n                "project_type",\n                "ouvrage_structure",\n            )\n            or "ouvrage_structure"\n        )\n\n'''

CENTRE_PROFILE_METHOD = '''    def _centre_profile(self) -> dict[str, str]:\n        project_type = self._project_type_key()\n\n        if project_type == "livre_textuel":\n            return {\n                "rail_title": "Structure du livre",\n                "rail_count": "page(s)",\n                "empty": "Aucune page",\n                "recent_tab": "Récentes",\n                "secondary_tab": "Chapitres",\n                "secondary_title": "Organisation du livre",\n                "secondary_text": "Manuscrit · Chapitres · Styles · Mise en page",\n            }\n\n        if project_type == "bande_dessinee":\n            return {\n                "rail_title": "Planches du livre",\n                "rail_count": "planche(s)",\n                "empty": "Aucune planche",\n                "recent_tab": "Récentes",\n                "secondary_tab": "Storyboard",\n                "secondary_title": "Organisation de la BD",\n                "secondary_text": "Storyboard · Planches · Cases · Bulles",\n            }\n\n        return {\n            "rail_title": "Chemin de fer",\n            "rail_count": "page(s)",\n            "empty": "Aucune page",\n            "recent_tab": "Récentes",\n            "secondary_tab": "Types",\n            "secondary_title": "Types de pages",\n            "secondary_text": "",\n        }\n\n'''

SPECIALIZED_SIDE_METHOD = '''    def _create_specialized_side_overview(\n        self,\n        parent,\n    ) -> ctk.CTkFrame:\n        profile = self._centre_profile()\n        frame = ctk.CTkFrame(\n            parent,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        frame.grid_columnconfigure(0, weight=1)\n\n        ctk.CTkLabel(\n            frame,\n            text=profile["secondary_title"],\n            font=(Fonts.FAMILY, 11, "bold"),\n            text_color=self.INK,\n            anchor="w",\n        ).grid(\n            row=0,\n            column=0,\n            sticky="ew",\n            padx=8,\n            pady=(10, 4),\n        )\n\n        ctk.CTkLabel(\n            frame,\n            text=profile["secondary_text"],\n            font=(Fonts.FAMILY, 8),\n            text_color=self.TEXT_MUTED,\n            justify="left",\n            anchor="w",\n            wraplength=245,\n        ).grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=8,\n            pady=(0, 10),\n        )\n\n        return frame\n\n'''


def fail(message: str) -> None:
    raise RuntimeError(message + "\nAucun fichier n'a été modifié.")


def function_bounds(text: str, name: str) -> tuple[int, int]:
    marker = f"    def {name}("
    start = text.find(marker)
    if start < 0:
        fail(f"Fonction introuvable : {name}")

    next_match = re.search(r"^    def [A-Za-z_][A-Za-z0-9_]*\(", text[start + len(marker):], re.M)
    if next_match is None:
        return start, len(text)
    end = start + len(marker) + next_match.start()
    return start, end


def replace_in_function(
    text: str,
    function_name: str,
    old: str,
    new: str,
    already_marker: str,
    label: str,
) -> str:
    start, end = function_bounds(text, function_name)
    block = text[start:end]

    if already_marker in block:
        return text

    if old not in block:
        fail(f"{label} : motif attendu introuvable")

    block = block.replace(old, new, 1)
    return text[:start] + block + text[end:]


def ensure_profiles(text: str) -> str:
    active_marker = "    def _active_workspaces("
    insert_at = text.find(active_marker)
    if insert_at < 0:
        fail(
            "Le ruban spécialisé n'est pas présent dans document_view.py "
            "(_active_workspaces introuvable)"
        )

    missing = ""
    if "    def _project_type_key(" not in text:
        missing += PROJECT_METHOD
    if "    def _centre_profile(" not in text:
        missing += CENTRE_PROFILE_METHOD

    if missing:
        text = text[:insert_at] + missing + text[insert_at:]
    return text


def adapt_tabs(text: str) -> str:
    if 'profile["secondary_tab"]' in text:
        return text

    old = '''        self._side_tab_buttons = {}\n        for column, (key, label) in enumerate(\n            (("recent", "Récentes"), ("types", "Types"))\n        ):\n'''
    new = '''        profile = self._centre_profile()\n\n        self._side_tab_buttons = {}\n        for column, (key, label) in enumerate(\n            (\n                ("recent", profile["recent_tab"]),\n                ("types", profile["secondary_tab"]),\n            )\n        ):\n'''

    if old not in text:
        fail("Onglets du panneau droit : motif attendu introuvable")
    return text.replace(old, new, 1)


def adapt_side_content(text: str) -> str:
    if "self._create_specialized_side_overview(" in text:
        return text

    old = '''        content = (\n            self._create_recent_pages(self._side_content)\n            if tab_key == "recent"\n            else self._create_categories(self._side_content)\n        )\n'''
    new = '''        if tab_key == "recent":\n            content = self._create_recent_pages(self._side_content)\n        elif self._project_type_key() == "ouvrage_structure":\n            content = self._create_categories(self._side_content)\n        else:\n            content = self._create_specialized_side_overview(\n                self._side_content\n            )\n'''

    if old not in text:
        fail("Contenu du panneau droit : motif attendu introuvable")
    return text.replace(old, new, 1)


def ensure_specialized_side_method(text: str) -> str:
    if "    def _create_specialized_side_overview(" in text:
        return text

    marker = "    def _create_rail_section("
    pos = text.find(marker)
    if pos < 0:
        fail("Point d'insertion du panneau spécialisé introuvable")
    return text[:pos] + SPECIALIZED_SIDE_METHOD + text[pos:]


def main() -> None:
    if not TARGET.is_file():
        raise SystemExit(
            "ERREUR : lance ce script depuis C:\\Users\\PC\\projet"
        )

    original = TARGET.read_text(encoding="utf-8")
    text = original

    text = ensure_profiles(text)
    text = adapt_tabs(text)
    text = adapt_side_content(text)
    text = ensure_specialized_side_method(text)

    text = replace_in_function(
        text,
        "_create_rail_section",
        '            text="Chemin de fer",\n',
        '            text=self._centre_profile()["rail_title"],\n',
        'text=self._centre_profile()["rail_title"]',
        "Titre central",
    )

    text = replace_in_function(
        text,
        "_create_rail_section",
        '            text=f"{len(self.pages)} page(s)",\n',
        '            text=(\n                f"{len(self.pages)} "\n                f"{self._centre_profile()[\'rail_count\']}"\n            ),\n',
        "rail_count",
        "Compteur central",
    )

    text = replace_in_function(
        text,
        "_populate_rail",
        '                text="Aucune page",\n',
        '                text=self._centre_profile()["empty"],\n',
        'self._centre_profile()["empty"]',
        "État vide central",
    )

    compile(text, str(TARGET), "exec")

    if text == original:
        print("CENTRE_PAR_TYPE_DEJA_CORRECT")
        print("Aucune modification nécessaire.")
        return

    backup_dir = Path("cache") / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_centre_type_{stamp}.py"
    shutil.copy2(TARGET, backup)

    TARGET.write_text(text, encoding="utf-8")

    pycache = TARGET.parent / "__pycache__"
    if pycache.exists():
        shutil.rmtree(pycache, ignore_errors=True)

    print("CENTRE_PAR_TYPE_V2_OK")
    print("Fichier modifié : src/gui/views/document_view.py")
    print(f"Sauvegarde : {backup}")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
