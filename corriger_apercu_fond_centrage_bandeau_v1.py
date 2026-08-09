from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"

REQUIRED_MARKERS = (
    "APERCU_MAQUETTAGE_GRANDE_VUE_SEULE_V1",
    "APERCU_CADRAGE_VERTICAL_CENTRE_V1",
)
NEW_MARKER = "APERCU_FOND_CONTINU_CENTRAGE_V1"

NEW_RENDER = '    def _render_preview_current_spread(self) -> None:\n        if self._preview_body is None:\n            return\n\n        for child in self._preview_body.winfo_children():\n            child.destroy()\n\n        if not self._preview_spreads:\n            ctk.CTkLabel(\n                self._preview_body,\n                text="Aucune page.",\n                font=Fonts.NORMAL,\n                text_color=self.TEXT_LIGHT,\n                fg_color=self.GROUP_BG,\n                corner_radius=6,\n            ).place(relx=0.5, rely=0.5, anchor="center")\n            self._update_preview_navigation()\n            return\n\n        self._preview_index = max(\n            0,\n            min(self._preview_index, len(self._preview_spreads) - 1),\n        )\n        left_item, right_item, left_number, right_number = (\n            self._preview_spreads[self._preview_index]\n        )\n\n        # Couverture et quatrième : une seule page réellement centrée.\n        # Pages intérieures : vraie double page côte à côte.\n        visible_pages = [\n            (left_item, left_number),\n            (right_item, right_number),\n        ]\n        visible_pages = [\n            (item, number)\n            for item, number in visible_pages\n            if item is not None\n        ]\n\n        # Conteneur à dimensions physiques fixes (Tk, pas CTk) :\n        # il n\'est donc plus agrandi par le facteur d\'échelle Windows.\n        # Son propre fond reprend le décor PageMaître et ne crée plus\n        # de plaque grise derrière les pages.\n        spread_width = 340 if len(visible_pages) == 1 else 662\n        spread_height = 484\n        spread = self._create_preview_background_canvas(\n            self._preview_body,\n            fixed_height=spread_height,\n        )\n        spread.configure(\n            width=spread_width,\n            borderwidth=0,\n            highlightthickness=0,\n        )\n        spread.place(relx=0.5, rely=0.5, anchor="center")\n        spread.grid_propagate(False)\n\n        if len(visible_pages) == 1:\n            item, number = visible_pages[0]\n            self._create_preview_large_page(\n                spread,\n                item,\n                number,\n            ).grid(row=0, column=0, padx=12, pady=14)\n        else:\n            spread.grid_columnconfigure(0, weight=1)\n            spread.grid_columnconfigure(1, weight=1)\n\n            self._create_preview_large_page(\n                spread,\n                left_item,\n                left_number,\n            ).grid(row=0, column=0, padx=(8, 7), pady=14)\n\n            self._create_preview_large_page(\n                spread,\n                right_item,\n                right_number,\n            ).grid(row=0, column=1, padx=(7, 8), pady=14)\n\n        self._update_preview_navigation()\n'
NEW_LARGE_PAGE = '    def _create_preview_large_page(\n        self,\n        parent,\n        item: dict[str, Any] | None,\n        page_number: int | None = None,\n    ) -> tk.Canvas:\n        # Canvas Tk : ses 316 x 456 restent des pixels réels.\n        # Cela évite le décalage vertical créé par un CTkFrame redimensionné\n        # par la mise à l\'échelle Windows. Le décor est affiché derrière\n        # la page au lieu d\'un rectangle gris opaque.\n        wrapper = self._create_preview_background_canvas(\n            parent,\n            fixed_height=456,\n        )\n        wrapper.configure(\n            width=316,\n            borderwidth=0,\n            highlightthickness=0,\n        )\n        wrapper.grid_propagate(False)\n        wrapper.grid_columnconfigure(0, weight=1)\n\n        if item is None:\n            return wrapper\n\n        definition = self._definition_for(\n            str(item.get("type", "autre"))\n        )\n        done = bool(item.get("done", False))\n        plan_group = self._plan_group_id(item)\n        group = self._group_for(plan_group)\n        accent = str(group.get("accent", self.INK))\n\n        page = tk.Frame(\n            wrapper,\n            width=300,\n            height=424,\n            background="#FFFFFF",\n            borderwidth=0,\n            highlightthickness=2 if done else 1,\n            highlightbackground=self.DONE if done else accent,\n            highlightcolor=self.DONE if done else accent,\n        )\n        page.grid(row=0, column=0, padx=8, pady=(4, 0))\n        page.grid_propagate(False)\n\n        photo = self._thumbnail_photo_for_definition(\n            definition,\n            subsample=1,\n        )\n\n        if photo is not None:\n            image_label = tk.Label(\n                page,\n                image=photo,\n                text="",\n                background="#FFFFFF",\n                borderwidth=0,\n                highlightthickness=0,\n            )\n            image_label.place(x=0, y=0, relwidth=1, relheight=1)\n            wrapper._preview_page_photo = photo\n        else:\n            fallback_color = self._plan_group_page_color(\n                plan_group,\n                str(definition.get("color", self.GROUP_BG)),\n            )\n            page.configure(background=fallback_color)\n            tk.Label(\n                page,\n                text=str(definition.get("symbol", "?")),\n                font=(Fonts.FAMILY, 40, "bold"),\n                foreground=accent,\n                background=fallback_color,\n                borderwidth=0,\n            ).place(relx=0.5, rely=0.45, anchor="center")\n\n        title = str(\n            item.get("title")\n            or definition.get("title", "Page")\n        )\n        caption = title\n        if page_number is not None:\n            caption = f"p. {page_number} · {title}"\n        if done:\n            caption = f"✓ {caption}"\n\n        ctk.CTkLabel(\n            wrapper,\n            text=caption,\n            height=24,\n            font=Fonts.SMALL,\n            text_color=self.DONE if done else self.INK,\n            fg_color=self.GROUP_BG,\n            corner_radius=5,\n            anchor="center",\n        ).grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=8,\n            pady=(4, 0),\n        )\n\n        return wrapper\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def get_method(text: str, name: str) -> str:
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.startswith(f"    def {name}("):
            start = i
            break
    if start is None:
        fail(f"méthode {name} introuvable")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("    def ") or lines[i].startswith("    @"):
            end = i
            break
    return "".join(lines[start:end])


def replace_method(text: str, name: str, block: str) -> str:
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.startswith(f"    def {name}("):
            start = i
            break
    if start is None:
        fail(f"méthode {name} introuvable")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("    def ") or lines[i].startswith("    @"):
            end = i
            break
    return "".join(lines[:start]) + block.rstrip() + "\n\n" + "".join(lines[end:])


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("APERCU_FOND_CONTINU_CENTRAGE_DEJA_APPLIQUE")
        return

    missing = [marker for marker in REQUIRED_MARKERS if marker not in original]
    if missing:
        fail("version attendue non détectée : " + ", ".join(missing))

    if 'text="Ensemble"' in original or '"overview"' in original:
        fail("Vue Ensemble est encore présente.")

    open_preview = get_method(original, "_open_preview")

    if "fixed_height=68" not in open_preview:
        fail("hauteur 68 du bandeau Aperçu introuvable")
    open_preview = open_preview.replace("fixed_height=68", "fixed_height=78", 1)

    old_group = """                width=width,
                height=60,
                fg_color=group_soft,
"""
    new_group = """                width=width,
                height=70,
                fg_color=group_soft,
"""
    if old_group not in open_preview:
        fail("hauteur 60 des groupes d'outils introuvable")
    open_preview = open_preview.replace(old_group, new_group, 1)

    marker_line = "        # APERCU_CADRAGE_VERTICAL_CENTRE_V1\n"
    if marker_line not in open_preview:
        fail("marqueur de cadrage vertical introuvable")
    open_preview = open_preview.replace(
        marker_line,
        marker_line + f"        # {NEW_MARKER}\n",
        1,
    )

    candidate = replace_method(original, "_open_preview", open_preview)
    candidate = replace_method(
        candidate,
        "_render_preview_current_spread",
        NEW_RENDER,
    )
    candidate = replace_method(
        candidate,
        "_create_preview_large_page",
        NEW_LARGE_PAGE,
    )

    # Les boutons restent strictement aux dimensions validées : 66 x 39.
    if "width=width,\n                height=39," not in open_preview:
        fail("dimensions validées des boutons Aperçu non détectées")

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_fond_continu_apercu_{stamp}.py"
    temporary = TARGET.with_suffix(".fond_continu.tmp")

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

    print("APERCU_FOND_CONTINU_CENTRAGE_OK")
    print("Boutons : dimensions validées 66 x 39 conservées.")
    print("Bandeau : hauteur 78, groupes d'outils 70.")
    print("Pages : centrage vertical corrigé sans effet d'échelle CTk.")
    print("Fond : décor PageMaître affiché derrière les pages, plaque grise supprimée.")
    print("Animation, pagination et taille des pages : inchangées.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
