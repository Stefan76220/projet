from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
EXPECTED_SHA256 = '875b92a2f4f597bc9a950fd7991d85aab8e0bd4218c82176be81634369ef5d62'
NEW_MARKER = "APERCU_ENSEMBLE_REALISTE_V1"

NEW_RENDER_OVERVIEW = '    def _render_preview_overview(self) -> None:\n        if self._preview_body is None:\n            return\n\n        # APERCU_ENSEMBLE_REALISTE_V1\n        # La vue Ensemble utilise toute la largeur disponible et présente\n        # plusieurs doubles pages par ligne avec les vraies miniatures.\n        scroll = ctk.CTkScrollableFrame(\n            self._preview_body,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        scroll.grid(\n            row=0,\n            column=0,\n            sticky="nsew",\n            padx=6,\n            pady=6,\n        )\n\n        if not self._preview_spreads:\n            ctk.CTkLabel(\n                scroll,\n                text="Aucune page.",\n                font=Fonts.NORMAL,\n                text_color=self.TEXT_LIGHT,\n                fg_color=self.GROUP_BG,\n                corner_radius=6,\n            ).grid(row=0, column=0, padx=20, pady=30)\n            return\n\n        try:\n            self._preview_body.update_idletasks()\n            available_width = int(self._preview_body.winfo_width())\n        except Exception:\n            available_width = 800\n\n        # 3 doubles pages sur la largeur validée de 840 px.\n        # Si l\'utilisateur réduit la fenêtre, la grille se replie proprement.\n        if available_width >= 720:\n            columns = 3\n        elif available_width >= 500:\n            columns = 2\n        else:\n            columns = 1\n\n        for column in range(columns):\n            scroll.grid_columnconfigure(\n                column,\n                weight=1,\n                uniform="overview_spreads",\n            )\n\n        for index, spread in enumerate(self._preview_spreads):\n            left_item, right_item, left_number, right_number = spread\n            row_number = index // columns\n            column_number = index % columns\n\n            self._create_preview_spread(\n                scroll,\n                left_item=left_item,\n                right_item=right_item,\n                left_page_number=left_number,\n                right_page_number=right_number,\n            ).grid(\n                row=row_number,\n                column=column_number,\n                padx=5,\n                pady=5,\n            )'
NEW_CREATE_SPREAD = '    def _create_preview_spread(\n        self,\n        parent,\n        left_item: dict[str, Any] | None,\n        right_item: dict[str, Any] | None,\n        left_page_number: int | None = None,\n        right_page_number: int | None = None,\n    ) -> ctk.CTkFrame:\n        reference_item = left_item or right_item\n        if reference_item is not None:\n            group_id = self._plan_group_id(reference_item)\n            group = self._group_for(group_id)\n            accent = str(group.get("accent", self.INK))\n        else:\n            accent = self.INK\n\n        soft = self._mix_color_with_white(accent, 0.88)\n        border = self._mix_color_with_white(accent, 0.58)\n\n        frame = ctk.CTkFrame(\n            parent,\n            width=226,\n            height=218,\n            fg_color=self.GROUP_BG,\n            corner_radius=6,\n            border_width=1,\n            border_color=border,\n        )\n        frame.grid_propagate(False)\n        frame.grid_columnconfigure(0, weight=1)\n\n        title_bar = ctk.CTkFrame(\n            frame,\n            height=24,\n            fg_color=soft,\n            corner_radius=5,\n        )\n        title_bar.grid(\n            row=0,\n            column=0,\n            sticky="ew",\n            padx=4,\n            pady=(4, 2),\n        )\n        title_bar.grid_propagate(False)\n\n        title = self._preview_spread_title(\n            left_item,\n            right_item,\n            left_page_number,\n            right_page_number,\n        )\n        ctk.CTkLabel(\n            title_bar,\n            text=title,\n            font=(Fonts.FAMILY, 9, "bold"),\n            text_color=accent,\n        ).place(relx=0, rely=0, relwidth=1, relheight=1)\n\n        pages = ctk.CTkFrame(\n            frame,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        pages.grid(\n            row=1,\n            column=0,\n            pady=(2, 4),\n        )\n\n        single_external_page = (\n            (left_item is None) != (right_item is None)\n            and left_page_number is None\n            and right_page_number is None\n        )\n\n        if single_external_page:\n            item = left_item or right_item\n            self._create_preview_page(\n                pages,\n                item,\n                None,\n            ).grid(\n                row=0,\n                column=0,\n                columnspan=2,\n                padx=3,\n                pady=0,\n            )\n        else:\n            self._create_preview_page(\n                pages,\n                left_item,\n                left_page_number,\n            ).grid(\n                row=0,\n                column=0,\n                padx=(3, 2),\n                pady=0,\n            )\n\n            self._create_preview_page(\n                pages,\n                right_item,\n                right_page_number,\n            ).grid(\n                row=0,\n                column=1,\n                padx=(2, 3),\n                pady=0,\n            )\n\n        return frame'
NEW_CREATE_PAGE = '    def _create_preview_page(\n        self,\n        parent,\n        item: dict[str, Any] | None,\n        page_number: int | None = None,\n    ) -> ctk.CTkFrame:\n        wrapper = ctk.CTkFrame(\n            parent,\n            width=104,\n            height=178,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        wrapper.grid_propagate(False)\n        wrapper.grid_columnconfigure(0, weight=1)\n\n        if item is None:\n            return wrapper\n\n        definition = self._definition_for(\n            str(item.get("type", "autre"))\n        )\n        done = bool(item.get("done", False))\n        plan_group = self._plan_group_id(item)\n        group = self._group_for(plan_group)\n        accent = str(group.get("accent", self.INK))\n\n        image_frame = tk.Frame(\n            wrapper,\n            width=100,\n            height=142,\n            background="#FFFFFF",\n            borderwidth=0,\n            highlightthickness=2 if done else 1,\n            highlightbackground=self.DONE if done else accent,\n            highlightcolor=self.DONE if done else accent,\n        )\n        image_frame.grid(\n            row=0,\n            column=0,\n            padx=2,\n            pady=(1, 0),\n        )\n        image_frame.grid_propagate(False)\n\n        photo = self._thumbnail_photo_for_definition(\n            definition,\n            subsample=3,\n        )\n\n        if photo is not None:\n            image_label = tk.Label(\n                image_frame,\n                image=photo,\n                text="",\n                background="#FFFFFF",\n                borderwidth=0,\n                highlightthickness=0,\n            )\n            image_label.place(relx=0.5, rely=0.5, anchor="center")\n            wrapper._overview_page_photo = photo\n        else:\n            fallback_color = self._plan_group_page_color(\n                plan_group,\n                str(definition.get("color", self.GROUP_BG)),\n            )\n            image_frame.configure(background=fallback_color)\n            tk.Label(\n                image_frame,\n                text=str(definition.get("symbol", "?")),\n                font=(Fonts.FAMILY, 20, "bold"),\n                foreground=accent,\n                background=fallback_color,\n                borderwidth=0,\n            ).place(relx=0.5, rely=0.5, anchor="center")\n\n        short_title = str(\n            definition.get("short")\n            or definition.get("title", "Page")\n        )\n        if page_number is not None:\n            caption = f"p. {page_number}\\n{short_title}"\n        else:\n            caption = short_title\n        if done:\n            caption = f"✓ {caption}"\n\n        ctk.CTkLabel(\n            wrapper,\n            text=caption,\n            width=100,\n            height=30,\n            font=(Fonts.FAMILY, 8),\n            text_color=self.DONE if done else self.INK,\n            justify="center",\n            anchor="center",\n        ).grid(\n            row=1,\n            column=0,\n            padx=2,\n            pady=(2, 0),\n        )\n\n        return wrapper'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_method(source_text: str, name: str, new_block: str) -> str:
    lines = source_text.splitlines(keepends=True)
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

    return "".join(lines[:start]) + new_block.rstrip() + "\n\n" + "".join(lines[end:])


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("APERCU_ENSEMBLE_REALISTE_DEJA_APPLIQUE")
        return

    current_hash = sha256(TARGET)
    if current_hash != EXPECTED_SHA256:
        fail(
            "mockup_view.py n'est plus exactement la version transmise. "
            "Par sécurité, aucune modification n'est appliquée. "
            f"SHA256 actuel : {current_hash}"
        )

    required = (
        "APERCU_GRANDE_VUE_V3",
        "APERCU_ROTATION_ALIGNEE_V1",
        "APERCU_FENETRE_CENTREE_V1",
    )
    missing = [marker for marker in required if marker not in original]
    if missing:
        fail(
            "version validée de la Grande vue non détectée : "
            + ", ".join(missing)
        )

    candidate = original
    candidate = replace_method(
        candidate,
        "_render_preview_overview",
        NEW_RENDER_OVERVIEW,
    )
    candidate = replace_method(
        candidate,
        "_create_preview_spread",
        NEW_CREATE_SPREAD,
    )
    candidate = replace_method(
        candidate,
        "_create_preview_page",
        NEW_CREATE_PAGE,
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
        / f"mockup_view_avant_vue_ensemble_realiste_{stamp}.py"
    )
    temporary = TARGET.with_suffix(".vue_ensemble_realiste.tmp")

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

    print("APERCU_ENSEMBLE_REALISTE_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Vue Ensemble : vraies miniatures de pages.")
    print("Disposition : 3 doubles pages par ligne à la largeur normale.")
    print("Fenêtre réduite : repli automatique en 2 puis 1 colonne.")
    print("Couverture et quatrième : affichées seules dans leur carte.")
    print("Ordre, pagination et logique recto-verso : inchangés.")
    print("Grande vue validée : aucune modification.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
