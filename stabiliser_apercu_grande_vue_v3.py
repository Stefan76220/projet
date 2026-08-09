from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
NEW_MARKER = "APERCU_GRANDE_VUE_V3"

STABLE_CANVAS_HELPER = '    def _create_preview_background_canvas(\n        self,\n        parent,\n        *,\n        fixed_height: int | None = None,\n    ) -> tk.Canvas:\n        """Fond stable de l\'Aperçu : l\'image reste un item du Canvas.\n\n        Les widgets sont de vraies fenêtres enfants du Canvas et ne peuvent\n        donc plus être recouverts par le redessin du fond.\n        """\n        canvas = tk.Canvas(\n            parent,\n            background=self.WINDOW_BG,\n            borderwidth=0,\n            highlightthickness=1,\n            highlightbackground=self.BORDER,\n        )\n        if fixed_height is not None:\n            canvas.configure(height=fixed_height)\n\n        canvas._preview_background_source = None\n        canvas._preview_background_photo = None\n        canvas._preview_background_item = None\n        canvas._preview_background_job = None\n\n        background_path = (\n            Path(__file__).resolve().parents[3]\n            / "assets"\n            / "interface"\n            / "backgrounds"\n            / "editorial_bg_soft.png"\n        )\n\n        if not background_path.is_file():\n            return canvas\n\n        try:\n            from PIL import Image, ImageTk\n\n            source = Image.open(background_path).convert("RGB")\n            canvas._preview_background_source = source\n            canvas._preview_background_item = canvas.create_image(\n                0,\n                0,\n                anchor="nw",\n            )\n\n            def redraw_now() -> None:\n                canvas._preview_background_job = None\n                try:\n                    width = max(1, int(canvas.winfo_width()))\n                    height = max(1, int(canvas.winfo_height()))\n                    if width <= 2 or height <= 2:\n                        return\n\n                    source_ratio = source.width / source.height\n                    target_ratio = width / height\n\n                    if target_ratio > source_ratio:\n                        resize_width = width\n                        resize_height = max(\n                            height,\n                            int(round(width / source_ratio)),\n                        )\n                    else:\n                        resize_height = height\n                        resize_width = max(\n                            width,\n                            int(round(height * source_ratio)),\n                        )\n\n                    resized = source.resize(\n                        (resize_width, resize_height),\n                        Image.Resampling.LANCZOS,\n                    )\n                    left = max(0, (resize_width - width) // 2)\n                    top = max(0, (resize_height - height) // 2)\n                    cropped = resized.crop(\n                        (left, top, left + width, top + height)\n                    )\n\n                    photo = ImageTk.PhotoImage(cropped)\n                    canvas._preview_background_photo = photo\n                    canvas.itemconfigure(\n                        canvas._preview_background_item,\n                        image=photo,\n                    )\n                    canvas.coords(\n                        canvas._preview_background_item,\n                        0,\n                        0,\n                    )\n                    canvas.tag_lower(canvas._preview_background_item)\n                except Exception:\n                    pass\n\n            def schedule_redraw(_event=None) -> None:\n                job = getattr(\n                    canvas,\n                    "_preview_background_job",\n                    None,\n                )\n                if job is not None:\n                    try:\n                        canvas.after_cancel(job)\n                    except Exception:\n                        pass\n                canvas._preview_background_job = canvas.after(\n                    35,\n                    redraw_now,\n                )\n\n            canvas.bind("<Configure>", schedule_redraw, add="+")\n            canvas.after_idle(redraw_now)\n        except Exception:\n            pass\n\n        return canvas'
NEW_OPEN_PREVIEW = '    def _open_preview(self) -> None:\n        if self._preview_window is not None:\n            try:\n                if self._preview_window.winfo_exists():\n                    self._preview_window.focus_force()\n                    self._preview_window.lift()\n                    return\n            except Exception:\n                self._preview_window = None\n\n        window = ctk.CTkToplevel(self.parent)\n        self._preview_window = window\n        window.title("Projet envisagé")\n\n        # APERCU_GRANDE_VUE_V3\n        # Fenêtre resserrée autour du livre : elle reste redimensionnable.\n        window.geometry("900x650")\n        window.minsize(780, 560)\n        window.configure(fg_color=self.WINDOW_BG)\n        window.protocol("WM_DELETE_WINDOW", self._close_preview)\n        window.grid_columnconfigure(0, weight=1)\n        window.grid_rowconfigure(2, weight=1)\n        window.bind("<Left>", lambda _event: self._show_previous_spread())\n        window.bind("<Right>", lambda _event: self._show_next_spread())\n\n        self._preview_animating = False\n        self._preview_turn_photo = None\n\n        header = ctk.CTkFrame(window, fg_color="transparent", height=32)\n        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 4))\n        header.grid_columnconfigure(0, weight=1)\n        header.grid_propagate(False)\n\n        ctk.CTkLabel(\n            header,\n            text="Projet envisagé",\n            font=Fonts.H2,\n            text_color=self.INK,\n        ).grid(row=0, column=0, sticky="w")\n\n        ctk.CTkLabel(\n            header,\n            text=self._preview_summary_text(),\n            font=Fonts.SMALL,\n            text_color=self.TEXT_MUTED,\n        ).grid(row=0, column=1, sticky="e")\n\n        # Canvas = fond stable. Il ne repasse jamais devant les outils.\n        ribbon = self._create_preview_background_canvas(\n            window,\n            fixed_height=68,\n        )\n        ribbon.grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=12,\n            pady=(0, 8),\n        )\n        ribbon.grid_propagate(False)\n\n        controls_row = ctk.CTkFrame(\n            ribbon,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        controls_row.place(relx=0.5, rely=0.5, anchor="center")\n\n        def preview_group(\n            title: str,\n            width: int,\n            accent: str,\n        ) -> tuple[ctk.CTkFrame, ctk.CTkFrame]:\n            group_soft = self._mix_color_with_white(accent, 0.91)\n            title_soft = self._mix_color_with_white(accent, 0.84)\n\n            group = ctk.CTkFrame(\n                controls_row,\n                width=width,\n                height=60,\n                fg_color=group_soft,\n                corner_radius=5,\n                border_width=1,\n                border_color=title_soft,\n            )\n            group.pack(side="left", fill="y", padx=2, pady=4)\n            group.pack_propagate(False)\n\n            controls = ctk.CTkFrame(\n                group,\n                fg_color="transparent",\n                height=40,\n            )\n            controls.pack(fill="x", padx=3, pady=(2, 0))\n            controls.pack_propagate(False)\n\n            title_bar = ctk.CTkFrame(\n                group,\n                height=16,\n                fg_color=title_soft,\n                corner_radius=0,\n            )\n            title_bar.pack(side="bottom", fill="x", padx=1, pady=(0, 1))\n            title_bar.pack_propagate(False)\n\n            ctk.CTkLabel(\n                title_bar,\n                text=title,\n                font=(Fonts.FAMILY, 9, "bold"),\n                text_color=accent,\n            ).place(relx=0, rely=0, relwidth=1, relheight=1)\n            return group, controls\n\n        def preview_button(\n            parent_frame,\n            icon: str,\n            label: str,\n            command,\n            width: int = 66,\n            accent: str | None = None,\n        ) -> ctk.CTkButton:\n            text_color = accent or self.INK\n            border = self._mix_color_with_white(text_color, 0.55)\n            button = ctk.CTkButton(\n                parent_frame,\n                text=f"{icon}\\n{label}",\n                width=width,\n                height=39,\n                corner_radius=5,\n                fg_color=self.GROUP_BG,\n                hover_color=self.ACCENT_SOFT,\n                text_color=text_color,\n                border_width=1,\n                border_color=border,\n                font=(Fonts.FAMILY, 9),\n                command=command,\n            )\n            button.pack(side="left", padx=1, pady=0)\n            return button\n\n        _, view_controls = preview_group("Vue", 140, self.LILAC)\n        self._preview_large_button = preview_button(\n            view_controls,\n            "▣",\n            "Grande vue",\n            lambda: self._set_preview_mode("large"),\n            accent=self.SKY,\n        )\n        self._preview_overview_button = preview_button(\n            view_controls,\n            "▦",\n            "Ensemble",\n            lambda: self._set_preview_mode("overview"),\n            accent=self.LILAC,\n        )\n\n        _, navigation_controls = preview_group(\n            "Navigation",\n            140,\n            self.SKY,\n        )\n        self._preview_previous_button = preview_button(\n            navigation_controls,\n            "◀",\n            "Précédent",\n            self._show_previous_spread,\n        )\n        self._preview_next_button = preview_button(\n            navigation_controls,\n            "▶",\n            "Suivant",\n            self._show_next_spread,\n        )\n\n        _, window_controls = preview_group(\n            "Fenêtre",\n            72,\n            self.CORAL,\n        )\n        preview_button(\n            window_controls,\n            "×",\n            "Fermer",\n            self._close_preview,\n            width=66,\n            accent=self.CORAL,\n        )\n\n        self._preview_body = self._create_preview_background_canvas(window)\n        self._preview_body.grid(\n            row=2,\n            column=0,\n            sticky="nsew",\n            padx=12,\n            pady=(0, 5),\n        )\n        self._preview_body.grid_columnconfigure(0, weight=1)\n        self._preview_body.grid_rowconfigure(0, weight=1)\n\n        self._preview_nav = ctk.CTkFrame(\n            window,\n            fg_color=self.GROUP_BG,\n            corner_radius=6,\n            height=28,\n            border_width=1,\n            border_color=self.BORDER,\n        )\n        self._preview_nav.grid(\n            row=3,\n            column=0,\n            sticky="ew",\n            padx=12,\n            pady=(0, 8),\n        )\n        self._preview_nav.grid_columnconfigure(0, weight=1)\n        self._preview_nav.grid_propagate(False)\n\n        self._preview_position_label = ctk.CTkLabel(\n            self._preview_nav,\n            text="",\n            font=Fonts.SMALL,\n            text_color=self.INK,\n        )\n        self._preview_position_label.grid(row=0, column=0)\n\n        self._preview_spreads = self._build_preview_spreads(\n            list(self._items())\n        )\n        self._preview_index = 0\n        self._set_preview_mode("large")\n        window.after(100, window.focus_force)'
NEW_ANIMATION = '    def _animate_preview_turn(\n        self,\n        direction: int,\n        target_index: int,\n    ) -> None:\n        """Tourne une feuille autour de la reliure avec ombre et verso."""\n        if self._preview_body is None:\n            return\n        if bool(getattr(self, "_preview_animating", False)):\n            return\n\n        current = self._preview_spreads[self._preview_index]\n        target = self._preview_spreads[target_index]\n\n        current_left, current_right, _, _ = current\n        target_left, target_right, _, _ = target\n\n        if direction > 0:\n            front_item = current_right or current_left\n            back_item = target_left or target_right\n        else:\n            front_item = current_left or current_right\n            back_item = target_right or target_left\n\n        if front_item is None:\n            self._preview_index = target_index\n            self._render_preview_current_spread()\n            return\n\n        def image_for(item):\n            if item is None:\n                return None\n            definition = self._definition_for(\n                str(item.get("type", "autre"))\n            )\n            path = self._thumbnail_path_for_definition(definition)\n            if path is None:\n                return None\n            try:\n                from PIL import Image\n                return Image.open(path).convert("RGB")\n            except Exception:\n                return None\n\n        front = image_for(front_item)\n        back = image_for(back_item)\n        if front is None:\n            self._preview_index = target_index\n            self._render_preview_current_spread()\n            return\n        if back is None:\n            back = front\n\n        try:\n            from PIL import Image, ImageEnhance, ImageTk\n\n            body = self._preview_body\n            body.update_idletasks()\n\n            body_width = max(640, int(body.winfo_width()))\n            body_height = max(460, int(body.winfo_height()))\n\n            page_height = min(424, max(320, body_height - 70))\n            page_width = max(\n                1,\n                int(round(page_height * 300 / 424)),\n            )\n            spine_x = body_width // 2\n            top_y = max(10, (body_height - page_height) // 2 - 6)\n\n            overlay = tk.Label(\n                body,\n                image="",\n                text="",\n                borderwidth=0,\n                highlightthickness=1,\n                highlightbackground="#B9B0A2",\n                background="#FFFFFF",\n            )\n            shadow = tk.Frame(\n                body,\n                background="#A69E93",\n                borderwidth=0,\n                highlightthickness=0,\n            )\n\n            self._preview_animating = True\n\n            if self._preview_previous_button is not None:\n                self._preview_previous_button.configure(state="disabled")\n            if self._preview_next_button is not None:\n                self._preview_next_button.configure(state="disabled")\n\n            # Plus lent et plus progressif que V2.\n            widths = [\n                1.00, 0.91, 0.80, 0.67, 0.53, 0.39, 0.26, 0.14, 0.06,\n                0.14, 0.26, 0.39, 0.53, 0.67, 0.80, 0.91, 1.00,\n            ]\n            middle = 8\n            delay = 24\n\n            def finish() -> None:\n                try:\n                    overlay.destroy()\n                except Exception:\n                    pass\n                try:\n                    shadow.destroy()\n                except Exception:\n                    pass\n\n                self._preview_animating = False\n                self._preview_index = target_index\n                self._render_preview_current_spread()\n\n            def draw(frame_index: int) -> None:\n                if frame_index >= len(widths):\n                    finish()\n                    return\n\n                ratio = widths[frame_index]\n                folded = 1.0 - ratio\n                width = max(10, int(round(page_width * ratio)))\n                height_loss = int(round(18 * folded))\n                height = max(40, page_height - height_loss)\n\n                use_back = frame_index > middle\n                source = back if use_back else front\n\n                page_image = source.resize(\n                    (width, height),\n                    Image.Resampling.LANCZOS,\n                )\n\n                # Assombrissement progressif vers la reliure.\n                brightness = 1.0 - 0.22 * folded\n                page_image = ImageEnhance.Brightness(\n                    page_image\n                ).enhance(brightness)\n\n                photo = ImageTk.PhotoImage(page_image)\n                self._preview_turn_photo = photo\n                overlay.configure(image=photo)\n\n                if direction > 0:\n                    x = spine_x if frame_index <= middle else spine_x - width\n                else:\n                    x = spine_x - width if frame_index <= middle else spine_x\n\n                y = top_y + max(0, (page_height - height) // 2)\n\n                shadow_width = max(\n                    2,\n                    min(16, int(round(16 * folded))),\n                )\n                if direction > 0:\n                    shadow_x = spine_x - shadow_width\n                else:\n                    shadow_x = spine_x\n\n                shadow.place(\n                    x=shadow_x,\n                    y=top_y + 3,\n                    width=shadow_width,\n                    height=page_height - 6,\n                )\n                overlay.place(\n                    x=x,\n                    y=y,\n                    width=width,\n                    height=height,\n                )\n                shadow.lift()\n                overlay.lift()\n\n                body.after(\n                    delay,\n                    lambda: draw(frame_index + 1),\n                )\n\n            draw(0)\n        except Exception:\n            self._preview_animating = False\n            self._preview_index = target_index\n            self._render_preview_current_spread()'


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
        if lines[index].startswith("    def ") or lines[index].startswith("    @"):
            end = index
            break

    return "".join(lines[:start]) + new_block.rstrip() + "\n\n" + "".join(lines[end:])


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("APERCU_GRANDE_VUE_V3_DEJA_APPLIQUE")
        return

    # Vérification structurelle de la V2 réellement installée.
    required = (
        "self._preview_animating = False",
        "controls_row.place(relx=0.5, rely=0.5, anchor=\"center\")",
        "def _animate_preview_turn(",
        "image bord à bord" if False else "wrapper = ctk.CTkFrame(",
    )
    missing = [part for part in required if part not in original]
    if missing:
        fail(
            "la Grande vue V2 attendue n'est pas détectée. "
            "Par sécurité, aucune modification n'est appliquée."
        )

    candidate = original

    open_anchor = "    def _open_preview(self) -> None:\n"
    if open_anchor not in candidate:
        fail("Aperçu introuvable")
    candidate = candidate.replace(
        open_anchor,
        STABLE_CANVAS_HELPER.rstrip() + "\n\n" + open_anchor,
        1,
    )

    candidate = replace_method(
        candidate,
        "_open_preview",
        NEW_OPEN_PREVIEW,
    )
    candidate = replace_method(
        candidate,
        "_animate_preview_turn",
        NEW_ANIMATION,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_apercu_grande_vue_v3_{stamp}.py"
    temporary = TARGET.with_suffix(".apercu_grande_vue_v3.tmp")

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

    print("APERCU_GRANDE_VUE_V3_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Fenêtre : réduite à 900 x 650 au démarrage.")
    print("Fond : rendu par Canvas stable, il ne peut plus recouvrir les outils.")
    print("Outils : restent centrés et visibles en permanence.")
    print("Animation : rotation plus progressive, ombre de reliure et changement de verso.")
    print("Pages et esthétique validées : conservées.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
