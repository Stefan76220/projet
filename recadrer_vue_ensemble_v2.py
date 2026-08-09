from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
EXPECTED_SHA256 = '9c84581583f42fef10834d7168f259692ffe1b32f13a4d0f343b282662b7dd84'
NEW_MARKER = "APERCU_ENSEMBLE_CADRE_V2"

NEW_SET_MODE = '    def _set_preview_mode(self, mode: str) -> None:\n        if self._preview_body is None:\n            return\n\n        self._preview_mode = "overview" if mode == "overview" else "large"\n\n        if self._preview_large_button is not None:\n            active = self._preview_mode == "large"\n            self._preview_large_button.configure(\n                fg_color=self.ACCENT_SOFT if active else self.GROUP_BG,\n                hover_color=self.ACCENT_SOFT,\n                text_color=self.INK if active else self.SKY,\n                border_color=self.INK if active else self.SKY,\n            )\n\n        if self._preview_overview_button is not None:\n            active = self._preview_mode == "overview"\n            self._preview_overview_button.configure(\n                fg_color="#EEEAF5" if active else self.GROUP_BG,\n                hover_color="#EEEAF5",\n                text_color=self.INK if active else self.LILAC,\n                border_color=self.INK if active else self.LILAC,\n            )\n\n        # APERCU_ENSEMBLE_CADRE_V2\n        # Nettoyage uniquement des éléments de la vue Ensemble.\n        try:\n            if isinstance(self._preview_body, tk.Canvas):\n                self._preview_body.delete("preview_overview")\n                self._preview_body.unbind("<MouseWheel>")\n        except Exception:\n            pass\n\n        configure_id = getattr(\n            self,\n            "_preview_overview_configure_bind_id",\n            None,\n        )\n        if configure_id is not None:\n            try:\n                self._preview_body.unbind("<Configure>", configure_id)\n            except Exception:\n                pass\n            self._preview_overview_configure_bind_id = None\n\n        for child in self._preview_body.winfo_children():\n            child.destroy()\n\n        if self._preview_mode == "overview":\n            if self._preview_nav is not None:\n                self._preview_nav.grid_remove()\n            self._render_preview_overview()\n        else:\n            if self._preview_nav is not None:\n                self._preview_nav.grid()\n            self._render_preview_current_spread()'
NEW_RENDER_OVERVIEW = '    def _render_preview_overview(self) -> None:\n        if self._preview_body is None:\n            return\n\n        # APERCU_ENSEMBLE_CADRE_V2\n        # Même esprit que Grande vue :\n        # - fond léger visible sur toute la surface ;\n        # - pages réelles bord à bord ;\n        # - titre sous chaque page ;\n        # - doubles pages présentées comme un livre ouvert ;\n        # - deux ensembles par ligne pour rester lisibles.\n        canvas = self._preview_body\n        if not isinstance(canvas, tk.Canvas):\n            return\n\n        canvas.delete("preview_overview")\n        canvas._overview_photos = []\n        if not hasattr(canvas, "_overview_photo_cache"):\n            canvas._overview_photo_cache = {}\n\n        old_scrollbar = getattr(self, "_preview_overview_scrollbar", None)\n        if old_scrollbar is not None:\n            try:\n                old_scrollbar.destroy()\n            except Exception:\n                pass\n\n        scrollbar = tk.Scrollbar(\n            canvas,\n            orient="vertical",\n            width=14,\n        )\n        scrollbar.place(\n            relx=1.0,\n            rely=0.0,\n            relheight=1.0,\n            anchor="ne",\n        )\n        self._preview_overview_scrollbar = scrollbar\n\n        self._preview_overview_offset = 0\n\n        if not self._preview_spreads:\n            canvas.create_text(\n                max(20, canvas.winfo_width() // 2),\n                50,\n                text="Aucune page.",\n                fill=self.TEXT_LIGHT,\n                font=Fonts.NORMAL,\n                tags=("preview_overview",),\n            )\n            return\n\n        def rgb_mix(color: str, white_ratio: float) -> str:\n            return self._mix_color_with_white(color, white_ratio)\n\n        def page_photo(item, width: int, height: int):\n            if item is None:\n                return None\n            definition = self._definition_for(\n                str(item.get("type", "autre"))\n            )\n            path = self._thumbnail_path_for_definition(definition)\n            if path is None:\n                return None\n\n            key = (str(path), width, height)\n            cache = canvas._overview_photo_cache\n            cached = cache.get(key)\n            if cached is not None:\n                return cached\n\n            try:\n                from PIL import Image, ImageTk\n\n                image = Image.open(path).convert("RGB")\n                image = image.resize(\n                    (width, height),\n                    Image.Resampling.LANCZOS,\n                )\n                photo = ImageTk.PhotoImage(image)\n                cache[key] = photo\n                return photo\n            except Exception:\n                return None\n\n        def draw_page(\n            item,\n            page_number,\n            center_x: int,\n            top_y: int,\n            page_width: int,\n            page_height: int,\n        ) -> None:\n            if item is None:\n                return\n\n            definition = self._definition_for(\n                str(item.get("type", "autre"))\n            )\n            group_id = self._plan_group_id(item)\n            group = self._group_for(group_id)\n            accent = str(group.get("accent", self.INK))\n            done = bool(item.get("done", False))\n            border = self.DONE if done else accent\n\n            left = center_x - page_width // 2\n            right = left + page_width\n            bottom = top_y + page_height\n\n            photo = page_photo(item, page_width, page_height)\n            if photo is not None:\n                canvas._overview_photos.append(photo)\n                canvas.create_image(\n                    center_x,\n                    top_y,\n                    image=photo,\n                    anchor="n",\n                    tags=("preview_overview",),\n                )\n            else:\n                fallback = self._plan_group_page_color(\n                    group_id,\n                    str(definition.get("color", self.GROUP_BG)),\n                )\n                canvas.create_rectangle(\n                    left,\n                    top_y,\n                    right,\n                    bottom,\n                    fill=fallback,\n                    outline="",\n                    tags=("preview_overview",),\n                )\n                canvas.create_text(\n                    center_x,\n                    top_y + page_height // 2,\n                    text=str(definition.get("symbol", "?")),\n                    fill=accent,\n                    font=(Fonts.FAMILY, 22, "bold"),\n                    tags=("preview_overview",),\n                )\n\n            # Cadre identique dans son principe à la Grande vue.\n            canvas.create_rectangle(\n                left,\n                top_y,\n                right,\n                bottom,\n                fill="",\n                outline=border,\n                width=2 if done else 1,\n                tags=("preview_overview",),\n            )\n\n            short_title = str(\n                definition.get("short")\n                or definition.get("title", "Page")\n            )\n            if page_number is not None:\n                caption = f"p. {page_number} · {short_title}"\n            else:\n                caption = short_title\n            if done:\n                caption = f"✓ {caption}"\n\n            caption_top = bottom + 5\n            canvas.create_rectangle(\n                left,\n                caption_top,\n                right,\n                caption_top + 24,\n                fill=self.GROUP_BG,\n                outline="",\n                tags=("preview_overview",),\n            )\n            canvas.create_text(\n                center_x,\n                caption_top + 12,\n                text=caption,\n                fill=self.DONE if done else self.INK,\n                font=(Fonts.FAMILY, 8),\n                width=max(60, page_width - 8),\n                justify="center",\n                tags=("preview_overview",),\n            )\n\n        def redraw() -> None:\n            if self._preview_mode != "overview":\n                return\n\n            canvas.delete("preview_overview")\n            canvas._overview_photos = []\n\n            try:\n                viewport_width = max(620, int(canvas.winfo_width()))\n                viewport_height = max(360, int(canvas.winfo_height()))\n            except Exception:\n                viewport_width = 800\n                viewport_height = 500\n\n            right_reserved = 22\n            usable_width = viewport_width - right_reserved\n\n            columns = 2 if usable_width >= 650 else 1\n            outer_margin = 18\n            column_gap = 18\n            cell_width = (\n                usable_width\n                - 2 * outer_margin\n                - (columns - 1) * column_gap\n            ) // columns\n\n            page_width = min(\n                132,\n                max(104, int((cell_width - 34) / 2)),\n            )\n            page_height = int(round(page_width * 424 / 300))\n            page_gap = 8\n\n            header_height = 28\n            caption_height = 31\n            row_gap = 22\n            cell_height = (\n                header_height\n                + page_height\n                + caption_height\n                + 18\n            )\n\n            rows = (\n                len(self._preview_spreads) + columns - 1\n            ) // columns\n            content_height = (\n                outer_margin\n                + rows * cell_height\n                + max(0, rows - 1) * row_gap\n                + outer_margin\n            )\n\n            max_offset = max(0, content_height - viewport_height)\n            offset = max(\n                0,\n                min(\n                    int(getattr(\n                        self,\n                        "_preview_overview_offset",\n                        0,\n                    )),\n                    max_offset,\n                ),\n            )\n            self._preview_overview_offset = offset\n\n            for index, spread in enumerate(self._preview_spreads):\n                row = index // columns\n                column = index % columns\n\n                x0 = (\n                    outer_margin\n                    + column * (cell_width + column_gap)\n                )\n                y0 = (\n                    outer_margin\n                    + row * (cell_height + row_gap)\n                    - offset\n                )\n                x1 = x0 + cell_width\n                y1 = y0 + cell_height\n\n                # Ignore les lignes entièrement hors écran.\n                if y1 < -20 or y0 > viewport_height + 20:\n                    continue\n\n                left_item, right_item, left_number, right_number = spread\n                reference_item = left_item or right_item\n\n                if reference_item is not None:\n                    group_id = self._plan_group_id(reference_item)\n                    group = self._group_for(group_id)\n                    accent = str(group.get("accent", self.INK))\n                else:\n                    accent = self.INK\n\n                border = rgb_mix(accent, 0.55)\n\n                # Cadre léger uniquement : le fond reste visible à l\'intérieur.\n                canvas.create_rectangle(\n                    x0,\n                    y0,\n                    x1,\n                    y1,\n                    fill="",\n                    outline=border,\n                    width=1,\n                    tags=("preview_overview",),\n                )\n\n                title = self._preview_spread_title(\n                    left_item,\n                    right_item,\n                    left_number,\n                    right_number,\n                )\n                canvas.create_text(\n                    (x0 + x1) // 2,\n                    y0 + 13,\n                    text=title,\n                    fill=accent,\n                    font=(Fonts.FAMILY, 9, "bold"),\n                    tags=("preview_overview",),\n                )\n\n                line_y = y0 + 26\n                canvas.create_line(\n                    x0 + 10,\n                    line_y,\n                    x1 - 10,\n                    line_y,\n                    fill=rgb_mix(accent, 0.70),\n                    width=1,\n                    tags=("preview_overview",),\n                )\n\n                pages_top = y0 + header_height + 5\n                single_external_page = (\n                    (left_item is None) != (right_item is None)\n                    and left_number is None\n                    and right_number is None\n                )\n\n                if single_external_page:\n                    item = left_item or right_item\n                    draw_page(\n                        item,\n                        None,\n                        (x0 + x1) // 2,\n                        pages_top,\n                        page_width,\n                        page_height,\n                    )\n                else:\n                    center = (x0 + x1) // 2\n                    left_center = (\n                        center - page_gap // 2 - page_width // 2\n                    )\n                    right_center = (\n                        center + page_gap // 2 + page_width // 2\n                    )\n\n                    draw_page(\n                        left_item,\n                        left_number,\n                        left_center,\n                        pages_top,\n                        page_width,\n                        page_height,\n                    )\n                    draw_page(\n                        right_item,\n                        right_number,\n                        right_center,\n                        pages_top,\n                        page_width,\n                        page_height,\n                    )\n\n                    # Reliure centrale : repère visuel discret.\n                    canvas.create_line(\n                        center,\n                        pages_top + 2,\n                        center,\n                        pages_top + page_height - 2,\n                        fill="#C8C0B5",\n                        width=1,\n                        tags=("preview_overview",),\n                    )\n\n            if max_offset <= 0:\n                scrollbar.set(0.0, 1.0)\n            else:\n                first = offset / content_height\n                last = min(\n                    1.0,\n                    (offset + viewport_height) / content_height,\n                )\n                scrollbar.set(first, last)\n\n            background_item = getattr(\n                canvas,\n                "_preview_background_item",\n                None,\n            )\n            if background_item is not None:\n                try:\n                    canvas.tag_lower(background_item)\n                except Exception:\n                    pass\n\n        def scroll_to(*args) -> None:\n            try:\n                viewport_height = max(360, int(canvas.winfo_height()))\n            except Exception:\n                viewport_height = 500\n\n            if args and args[0] == "moveto":\n                # Recalcule une approximation stable, redraw ajuste ensuite.\n                fraction = float(args[1])\n                rows = max(1, (len(self._preview_spreads) + 1) // 2)\n                estimated_height = rows * 250\n                max_offset = max(0, estimated_height - viewport_height)\n                self._preview_overview_offset = int(\n                    fraction * max_offset\n                )\n            elif args and args[0] == "scroll":\n                amount = int(args[1])\n                mode = str(args[2])\n                step = (\n                    int(viewport_height * 0.75)\n                    if mode == "pages"\n                    else 56\n                )\n                self._preview_overview_offset = int(\n                    getattr(\n                        self,\n                        "_preview_overview_offset",\n                        0,\n                    )\n                ) + amount * step\n            redraw()\n\n        scrollbar.configure(command=scroll_to)\n\n        def mousewheel(event) -> None:\n            delta = int(getattr(event, "delta", 0))\n            if delta == 0:\n                return\n            direction = -1 if delta > 0 else 1\n            self._preview_overview_offset = int(\n                getattr(\n                    self,\n                    "_preview_overview_offset",\n                    0,\n                )\n            ) + direction * 56\n            redraw()\n\n        canvas.bind("<MouseWheel>", mousewheel)\n\n        old_bind = getattr(\n            self,\n            "_preview_overview_configure_bind_id",\n            None,\n        )\n        if old_bind is not None:\n            try:\n                canvas.unbind("<Configure>", old_bind)\n            except Exception:\n                pass\n\n        def on_resize(_event=None) -> None:\n            if self._preview_mode == "overview":\n                canvas.after_idle(redraw)\n\n        self._preview_overview_configure_bind_id = canvas.bind(\n            "<Configure>",\n            on_resize,\n            add="+",\n        )\n\n        redraw()'


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

    return "".join(lines[:start]) + new_block.rstrip() + "\n\n" + "".join(lines[end:])


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("APERCU_ENSEMBLE_CADRE_V2_DEJA_APPLIQUE")
        return

    current_hash = sha256(TARGET)
    if current_hash != EXPECTED_SHA256:
        fail(
            "mockup_view.py n'est plus exactement la version attendue. "
            "Par sécurité, aucune modification n'est appliquée. "
            f"SHA256 actuel : {current_hash}"
        )

    required = (
        "APERCU_ENSEMBLE_REALISTE_V1",
        "APERCU_GRANDE_VUE_V3",
        "APERCU_ROTATION_ALIGNEE_V1",
        "APERCU_FENETRE_CENTREE_V1",
    )
    missing = [marker for marker in required if marker not in original]
    if missing:
        fail(
            "version attendue non détectée : "
            + ", ".join(missing)
        )

    candidate = original
    candidate = replace_method(
        candidate,
        "_set_preview_mode",
        NEW_SET_MODE,
    )
    candidate = replace_method(
        candidate,
        "_render_preview_overview",
        NEW_RENDER_OVERVIEW,
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
        / f"mockup_view_avant_vue_ensemble_cadree_v2_{stamp}.py"
    )
    temporary = TARGET.with_suffix(".vue_ensemble_cadree_v2.tmp")

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

    print("APERCU_ENSEMBLE_CADRE_V2_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Fond : visible sur toute la surface de Vue Ensemble.")
    print("Disposition : 2 doubles pages par ligne, lecture gauche-droite.")
    print("Pages : vraies miniatures bord à bord dans leur cadre.")
    print("Titres : placés sous chaque page, comme en Grande vue.")
    print("Couverture et quatrième : centrées seules.")
    print("Cadres : fins, sans grands panneaux opaques.")
    print("Grande vue validée : inchangée.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
