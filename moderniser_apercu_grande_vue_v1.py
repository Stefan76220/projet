from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
EXPECTED_SHA256 = '939d48706d01351b41832a25667841b065d7bf4e7244d0d73d7e8f9b3dabc72e'

REQUIRED_MARKERS = (
    "MINIATURES_REALISTES_V1",
    "RUBAN_PAINT_SANS_MINIATURES_V1",
    "FOND_VISIBLE_RUBAN_PLAN_V1",
)
NEW_MARKER = "APERCU_GRANDE_VUE_V1"

NEW_OPEN_PREVIEW = '    def _open_preview(self) -> None:\n        if self._preview_window is not None:\n            try:\n                if self._preview_window.winfo_exists():\n                    self._preview_window.focus_force()\n                    self._preview_window.lift()\n                    return\n            except Exception:\n                self._preview_window = None\n\n        window = ctk.CTkToplevel(self.parent)\n        self._preview_window = window\n        window.title("Projet envisagé")\n        window.geometry("1000x720")\n        window.minsize(800, 560)\n        window.configure(fg_color=self.WINDOW_BG)\n        window.protocol("WM_DELETE_WINDOW", self._close_preview)\n        window.grid_columnconfigure(0, weight=1)\n        window.grid_rowconfigure(2, weight=1)\n        window.bind("<Left>", lambda _event: self._show_previous_spread())\n        window.bind("<Right>", lambda _event: self._show_next_spread())\n\n        header = ctk.CTkFrame(window, fg_color="transparent", height=32)\n        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 4))\n        header.grid_columnconfigure(0, weight=1)\n        header.grid_propagate(False)\n\n        ctk.CTkLabel(\n            header,\n            text="Projet envisagé",\n            font=Fonts.H2,\n            text_color=self.INK,\n        ).grid(row=0, column=0, sticky="w")\n\n        ctk.CTkLabel(\n            header,\n            text=self._preview_summary_text(),\n            font=Fonts.SMALL,\n            text_color=self.TEXT_MUTED,\n        ).grid(row=0, column=1, sticky="e")\n\n        # APERCU_GRANDE_VUE_V1\n        # Même logique visuelle que le Bureau de maquettage :\n        # fond léger visible, groupes compacts, boutons 66 x 39.\n        ribbon = self._create_soft_background_container(window)\n        ribbon.configure(\n            highlightthickness=1,\n            highlightbackground=self.BORDER,\n        )\n        ribbon.grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=12,\n            pady=(0, 8),\n        )\n        ribbon.configure(height=68)\n        ribbon.grid_propagate(False)\n\n        def preview_group(\n            title: str,\n            width: int,\n            accent: str,\n        ) -> tuple[ctk.CTkFrame, ctk.CTkFrame]:\n            group_soft = self._mix_color_with_white(accent, 0.91)\n            title_soft = self._mix_color_with_white(accent, 0.84)\n\n            group = ctk.CTkFrame(\n                ribbon,\n                width=width,\n                height=60,\n                fg_color=group_soft,\n                corner_radius=5,\n                border_width=1,\n                border_color=title_soft,\n            )\n            group.pack(side="left", fill="y", padx=(4, 1), pady=4)\n            group.pack_propagate(False)\n\n            controls = ctk.CTkFrame(\n                group,\n                fg_color="transparent",\n                height=40,\n            )\n            controls.pack(fill="x", padx=3, pady=(2, 0))\n            controls.pack_propagate(False)\n\n            title_bar = ctk.CTkFrame(\n                group,\n                height=16,\n                fg_color=title_soft,\n                corner_radius=0,\n            )\n            title_bar.pack(side="bottom", fill="x", padx=1, pady=(0, 1))\n            title_bar.pack_propagate(False)\n\n            ctk.CTkLabel(\n                title_bar,\n                text=title,\n                font=(Fonts.FAMILY, 9, "bold"),\n                text_color=accent,\n            ).place(relx=0, rely=0, relwidth=1, relheight=1)\n            return group, controls\n\n        def preview_button(\n            parent_frame,\n            icon: str,\n            label: str,\n            command,\n            width: int = 66,\n            accent: str | None = None,\n        ) -> ctk.CTkButton:\n            text_color = accent or self.INK\n            border = self._mix_color_with_white(\n                text_color,\n                0.55,\n            )\n            button = ctk.CTkButton(\n                parent_frame,\n                text=f"{icon}\\n{label}",\n                width=width,\n                height=39,\n                corner_radius=5,\n                fg_color=self.GROUP_BG,\n                hover_color=self.ACCENT_SOFT,\n                text_color=text_color,\n                border_width=1,\n                border_color=border,\n                font=(Fonts.FAMILY, 9),\n                command=command,\n            )\n            button.pack(side="left", padx=1, pady=0)\n            return button\n\n        _, view_controls = preview_group("Vue", 140, self.LILAC)\n        self._preview_large_button = preview_button(\n            view_controls,\n            "▣",\n            "Grande vue",\n            lambda: self._set_preview_mode("large"),\n            accent=self.SKY,\n        )\n        self._preview_overview_button = preview_button(\n            view_controls,\n            "▦",\n            "Ensemble",\n            lambda: self._set_preview_mode("overview"),\n            accent=self.LILAC,\n        )\n\n        _, navigation_controls = preview_group(\n            "Navigation",\n            140,\n            self.SKY,\n        )\n        self._preview_previous_button = preview_button(\n            navigation_controls,\n            "◀",\n            "Précédent",\n            self._show_previous_spread,\n        )\n        self._preview_next_button = preview_button(\n            navigation_controls,\n            "▶",\n            "Suivant",\n            self._show_next_spread,\n        )\n\n        _, window_controls = preview_group(\n            "Fenêtre",\n            72,\n            self.CORAL,\n        )\n        preview_button(\n            window_controls,\n            "×",\n            "Fermer",\n            self._close_preview,\n            width=66,\n            accent=self.CORAL,\n        )\n\n        self._preview_body = self._create_soft_background_container(window)\n        self._preview_body.configure(\n            highlightthickness=1,\n            highlightbackground=self.BORDER,\n        )\n        self._preview_body.grid(\n            row=2,\n            column=0,\n            sticky="nsew",\n            padx=12,\n            pady=(0, 5),\n        )\n        self._preview_body.grid_columnconfigure(0, weight=1)\n        self._preview_body.grid_rowconfigure(0, weight=1)\n\n        self._preview_nav = ctk.CTkFrame(\n            window,\n            fg_color=self.GROUP_BG,\n            corner_radius=6,\n            height=28,\n            border_width=1,\n            border_color=self.BORDER,\n        )\n        self._preview_nav.grid(\n            row=3,\n            column=0,\n            sticky="ew",\n            padx=12,\n            pady=(0, 8),\n        )\n        self._preview_nav.grid_columnconfigure(0, weight=1)\n        self._preview_nav.grid_propagate(False)\n\n        self._preview_position_label = ctk.CTkLabel(\n            self._preview_nav,\n            text="",\n            font=Fonts.SMALL,\n            text_color=self.INK,\n        )\n        self._preview_position_label.grid(row=0, column=0)\n\n        self._preview_spreads = self._build_preview_spreads(\n            list(self._items())\n        )\n        self._preview_index = 0\n        self._set_preview_mode("large")\n        window.after(100, window.focus_force)'
NEW_RENDER_CURRENT = '    def _render_preview_current_spread(self) -> None:\n        if self._preview_body is None:\n            return\n\n        for child in self._preview_body.winfo_children():\n            child.destroy()\n\n        if not self._preview_spreads:\n            ctk.CTkLabel(\n                self._preview_body,\n                text="Aucune page.",\n                font=Fonts.NORMAL,\n                text_color=self.TEXT_LIGHT,\n                fg_color=self.GROUP_BG,\n                corner_radius=6,\n            ).grid(row=0, column=0, padx=20, pady=30)\n            self._update_preview_navigation()\n            return\n\n        self._preview_index = max(\n            0,\n            min(self._preview_index, len(self._preview_spreads) - 1),\n        )\n        left_item, right_item, left_number, right_number = (\n            self._preview_spreads[self._preview_index]\n        )\n\n        spread = ctk.CTkFrame(\n            self._preview_body,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        spread.grid(row=0, column=0)\n\n        # Couverture et quatrième : une seule page réellement centrée.\n        # Pages intérieures : vraie double page côte à côte.\n        visible_pages = [\n            (left_item, left_number),\n            (right_item, right_number),\n        ]\n        visible_pages = [\n            (item, number)\n            for item, number in visible_pages\n            if item is not None\n        ]\n\n        if len(visible_pages) == 1:\n            item, number = visible_pages[0]\n            self._create_preview_large_page(\n                spread,\n                item,\n                number,\n            ).grid(row=0, column=0, padx=12, pady=14)\n        else:\n            spread.grid_columnconfigure(0, weight=1)\n            spread.grid_columnconfigure(1, weight=1)\n\n            self._create_preview_large_page(\n                spread,\n                left_item,\n                left_number,\n            ).grid(row=0, column=0, padx=(8, 7), pady=14)\n\n            self._create_preview_large_page(\n                spread,\n                right_item,\n                right_number,\n            ).grid(row=0, column=1, padx=(7, 8), pady=14)\n\n        self._update_preview_navigation()'
NEW_LARGE_PAGE = '    def _create_preview_large_page(\n        self,\n        parent,\n        item: dict[str, Any] | None,\n        page_number: int | None = None,\n    ) -> ctk.CTkFrame:\n        if item is None:\n            empty = ctk.CTkFrame(\n                parent,\n                width=316,\n                height=458,\n                fg_color="transparent",\n                corner_radius=0,\n            )\n            empty.grid_propagate(False)\n            return empty\n\n        definition = self._definition_for(\n            str(item.get("type", "autre"))\n        )\n        done = bool(item.get("done", False))\n        plan_group = self._plan_group_id(item)\n        group = self._group_for(plan_group)\n        accent = str(group.get("accent", self.INK))\n\n        page = ctk.CTkFrame(\n            parent,\n            width=316,\n            height=458,\n            fg_color=self.GROUP_BG,\n            corner_radius=4,\n            border_width=2 if done else 1,\n            border_color=self.DONE if done else accent,\n        )\n        page.grid_propagate(False)\n        page.grid_columnconfigure(0, weight=1)\n\n        image_holder = tk.Frame(\n            page,\n            width=300,\n            height=424,\n            background="#FFFFFF",\n            borderwidth=0,\n            highlightthickness=0,\n        )\n        image_holder.grid(\n            row=0,\n            column=0,\n            padx=7,\n            pady=(7, 2),\n        )\n        image_holder.grid_propagate(False)\n\n        photo = self._thumbnail_photo_for_definition(\n            definition,\n            subsample=1,\n        )\n\n        if photo is not None:\n            image_label = tk.Label(\n                image_holder,\n                image=photo,\n                text="",\n                background="#FFFFFF",\n                borderwidth=0,\n                highlightthickness=0,\n            )\n            image_label.place(relx=0.5, rely=0.5, anchor="center")\n            page._preview_page_photo = photo\n        else:\n            fallback_color = self._plan_group_page_color(\n                plan_group,\n                str(definition.get("color", self.GROUP_BG)),\n            )\n            image_holder.configure(background=fallback_color)\n\n            tk.Label(\n                image_holder,\n                text=str(definition.get("symbol", "?")),\n                font=(Fonts.FAMILY, 40, "bold"),\n                foreground=accent,\n                background=fallback_color,\n                borderwidth=0,\n            ).place(relx=0.5, rely=0.43, anchor="center")\n\n            tk.Label(\n                image_holder,\n                text=str(\n                    item.get("title")\n                    or definition.get("title", "Page")\n                ),\n                font=Fonts.NORMAL,\n                foreground=self.INK,\n                background=fallback_color,\n                borderwidth=0,\n            ).place(relx=0.5, rely=0.56, anchor="center")\n\n        title = str(\n            item.get("title")\n            or definition.get("title", "Page")\n        )\n        if page_number is not None:\n            caption = f"p. {page_number} · {title}"\n        else:\n            caption = title\n        if done:\n            caption = f"✓ {caption}"\n\n        ctk.CTkLabel(\n            page,\n            text=caption,\n            height=20,\n            font=Fonts.SMALL,\n            text_color=self.DONE if done else self.INK,\n            anchor="center",\n        ).grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=6,\n            pady=(0, 3),\n        )\n\n        return page'


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
        print("APERCU_GRANDE_VUE_DEJA_APPLIQUE")
        return

    current_hash = sha256(TARGET)
    if current_hash != EXPECTED_SHA256:
        fail(
            "mockup_view.py n'est plus exactement la version que vous venez "
            "de transmettre. Par sécurité, aucune modification n'est appliquée. "
            f"SHA256 actuel : {current_hash}"
        )

    missing = [marker for marker in REQUIRED_MARKERS if marker not in original]
    if missing:
        fail("version attendue non détectée : " + ", ".join(missing))

    candidate = original
    candidate = replace_method(
        candidate,
        "_open_preview",
        NEW_OPEN_PREVIEW,
    )
    candidate = replace_method(
        candidate,
        "_render_preview_current_spread",
        NEW_RENDER_CURRENT,
    )
    candidate = replace_method(
        candidate,
        "_create_preview_large_page",
        NEW_LARGE_PAGE,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_apercu_grande_vue_{stamp}.py"
    temporary = TARGET.with_suffix(".apercu_grande_vue.tmp")

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

    print("APERCU_GRANDE_VUE_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Grande vue : vraie miniature 300 x 424 px affichée comme page.")
    print("Couverture et quatrième : page unique centrée.")
    print("Pages intérieures : double page côte à côte.")
    print("Ruban de l'Aperçu : boutons 66 x 39, esprit Paint.")
    print("Fond discret : appliqué au ruban et à la zone d'Aperçu.")
    print("Vue Ensemble : logique actuelle conservée pour l'étape suivante.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
