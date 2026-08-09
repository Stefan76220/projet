from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"

REQUIRED_MARKER = "APERCU_GRANDE_VUE_V1"
NEW_MARKER = "APERCU_GRANDE_VUE_V2"

NEW_OPEN_PREVIEW = '    def _open_preview(self) -> None:\n        if self._preview_window is not None:\n            try:\n                if self._preview_window.winfo_exists():\n                    self._preview_window.focus_force()\n                    self._preview_window.lift()\n                    return\n            except Exception:\n                self._preview_window = None\n\n        window = ctk.CTkToplevel(self.parent)\n        self._preview_window = window\n        window.title("Projet envisagé")\n        window.geometry("1000x720")\n        window.minsize(800, 560)\n        window.configure(fg_color=self.WINDOW_BG)\n        window.protocol("WM_DELETE_WINDOW", self._close_preview)\n        window.grid_columnconfigure(0, weight=1)\n        window.grid_rowconfigure(2, weight=1)\n        window.bind("<Left>", lambda _event: self._show_previous_spread())\n        window.bind("<Right>", lambda _event: self._show_next_spread())\n\n        self._preview_animating = False\n        self._preview_turn_photo = None\n\n        header = ctk.CTkFrame(window, fg_color="transparent", height=32)\n        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 4))\n        header.grid_columnconfigure(0, weight=1)\n        header.grid_propagate(False)\n\n        ctk.CTkLabel(\n            header,\n            text="Projet envisagé",\n            font=Fonts.H2,\n            text_color=self.INK,\n        ).grid(row=0, column=0, sticky="w")\n\n        ctk.CTkLabel(\n            header,\n            text=self._preview_summary_text(),\n            font=Fonts.SMALL,\n            text_color=self.TEXT_MUTED,\n        ).grid(row=0, column=1, sticky="e")\n\n        ribbon = self._create_soft_background_container(window)\n        ribbon.configure(\n            highlightthickness=1,\n            highlightbackground=self.BORDER,\n        )\n        ribbon.grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=12,\n            pady=(0, 8),\n        )\n        ribbon.configure(height=68)\n        ribbon.grid_propagate(False)\n\n        controls_row = ctk.CTkFrame(\n            ribbon,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        controls_row.place(relx=0.5, rely=0.5, anchor="center")\n\n        def preview_group(\n            title: str,\n            width: int,\n            accent: str,\n        ) -> tuple[ctk.CTkFrame, ctk.CTkFrame]:\n            group_soft = self._mix_color_with_white(accent, 0.91)\n            title_soft = self._mix_color_with_white(accent, 0.84)\n\n            group = ctk.CTkFrame(\n                controls_row,\n                width=width,\n                height=60,\n                fg_color=group_soft,\n                corner_radius=5,\n                border_width=1,\n                border_color=title_soft,\n            )\n            group.pack(side="left", fill="y", padx=2, pady=4)\n            group.pack_propagate(False)\n\n            controls = ctk.CTkFrame(\n                group,\n                fg_color="transparent",\n                height=40,\n            )\n            controls.pack(fill="x", padx=3, pady=(2, 0))\n            controls.pack_propagate(False)\n\n            title_bar = ctk.CTkFrame(\n                group,\n                height=16,\n                fg_color=title_soft,\n                corner_radius=0,\n            )\n            title_bar.pack(side="bottom", fill="x", padx=1, pady=(0, 1))\n            title_bar.pack_propagate(False)\n\n            ctk.CTkLabel(\n                title_bar,\n                text=title,\n                font=(Fonts.FAMILY, 9, "bold"),\n                text_color=accent,\n            ).place(relx=0, rely=0, relwidth=1, relheight=1)\n            return group, controls\n\n        def preview_button(\n            parent_frame,\n            icon: str,\n            label: str,\n            command,\n            width: int = 66,\n            accent: str | None = None,\n        ) -> ctk.CTkButton:\n            text_color = accent or self.INK\n            border = self._mix_color_with_white(text_color, 0.55)\n            button = ctk.CTkButton(\n                parent_frame,\n                text=f"{icon}\\n{label}",\n                width=width,\n                height=39,\n                corner_radius=5,\n                fg_color=self.GROUP_BG,\n                hover_color=self.ACCENT_SOFT,\n                text_color=text_color,\n                border_width=1,\n                border_color=border,\n                font=(Fonts.FAMILY, 9),\n                command=command,\n            )\n            button.pack(side="left", padx=1, pady=0)\n            return button\n\n        _, view_controls = preview_group("Vue", 140, self.LILAC)\n        self._preview_large_button = preview_button(\n            view_controls,\n            "▣",\n            "Grande vue",\n            lambda: self._set_preview_mode("large"),\n            accent=self.SKY,\n        )\n        self._preview_overview_button = preview_button(\n            view_controls,\n            "▦",\n            "Ensemble",\n            lambda: self._set_preview_mode("overview"),\n            accent=self.LILAC,\n        )\n\n        _, navigation_controls = preview_group(\n            "Navigation",\n            140,\n            self.SKY,\n        )\n        self._preview_previous_button = preview_button(\n            navigation_controls,\n            "◀",\n            "Précédent",\n            self._show_previous_spread,\n        )\n        self._preview_next_button = preview_button(\n            navigation_controls,\n            "▶",\n            "Suivant",\n            self._show_next_spread,\n        )\n\n        _, window_controls = preview_group(\n            "Fenêtre",\n            72,\n            self.CORAL,\n        )\n        preview_button(\n            window_controls,\n            "×",\n            "Fermer",\n            self._close_preview,\n            width=66,\n            accent=self.CORAL,\n        )\n\n        self._preview_body = self._create_soft_background_container(window)\n        self._preview_body.configure(\n            highlightthickness=1,\n            highlightbackground=self.BORDER,\n        )\n        self._preview_body.grid(\n            row=2,\n            column=0,\n            sticky="nsew",\n            padx=12,\n            pady=(0, 5),\n        )\n        self._preview_body.grid_columnconfigure(0, weight=1)\n        self._preview_body.grid_rowconfigure(0, weight=1)\n\n        self._preview_nav = ctk.CTkFrame(\n            window,\n            fg_color=self.GROUP_BG,\n            corner_radius=6,\n            height=28,\n            border_width=1,\n            border_color=self.BORDER,\n        )\n        self._preview_nav.grid(\n            row=3,\n            column=0,\n            sticky="ew",\n            padx=12,\n            pady=(0, 8),\n        )\n        self._preview_nav.grid_columnconfigure(0, weight=1)\n        self._preview_nav.grid_propagate(False)\n\n        self._preview_position_label = ctk.CTkLabel(\n            self._preview_nav,\n            text="",\n            font=Fonts.SMALL,\n            text_color=self.INK,\n        )\n        self._preview_position_label.grid(row=0, column=0)\n\n        self._preview_spreads = self._build_preview_spreads(\n            list(self._items())\n        )\n        self._preview_index = 0\n        self._set_preview_mode("large")\n        window.after(100, window.focus_force)'
NEW_LARGE_PAGE = '    def _create_preview_large_page(\n        self,\n        parent,\n        item: dict[str, Any] | None,\n        page_number: int | None = None,\n    ) -> ctk.CTkFrame:\n        wrapper = ctk.CTkFrame(\n            parent,\n            width=316,\n            height=456,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        wrapper.grid_propagate(False)\n        wrapper.grid_columnconfigure(0, weight=1)\n\n        if item is None:\n            return wrapper\n\n        definition = self._definition_for(\n            str(item.get("type", "autre"))\n        )\n        done = bool(item.get("done", False))\n        plan_group = self._plan_group_id(item)\n        group = self._group_for(plan_group)\n        accent = str(group.get("accent", self.INK))\n\n        page = tk.Frame(\n            wrapper,\n            width=300,\n            height=424,\n            background="#FFFFFF",\n            borderwidth=0,\n            highlightthickness=2 if done else 1,\n            highlightbackground=self.DONE if done else accent,\n            highlightcolor=self.DONE if done else accent,\n        )\n        page.grid(row=0, column=0, padx=8, pady=(4, 0))\n        page.grid_propagate(False)\n\n        photo = self._thumbnail_photo_for_definition(\n            definition,\n            subsample=1,\n        )\n\n        if photo is not None:\n            image_label = tk.Label(\n                page,\n                image=photo,\n                text="",\n                background="#FFFFFF",\n                borderwidth=0,\n                highlightthickness=0,\n            )\n            image_label.place(x=0, y=0, relwidth=1, relheight=1)\n            wrapper._preview_page_photo = photo\n        else:\n            fallback_color = self._plan_group_page_color(\n                plan_group,\n                str(definition.get("color", self.GROUP_BG)),\n            )\n            page.configure(background=fallback_color)\n            tk.Label(\n                page,\n                text=str(definition.get("symbol", "?")),\n                font=(Fonts.FAMILY, 40, "bold"),\n                foreground=accent,\n                background=fallback_color,\n                borderwidth=0,\n            ).place(relx=0.5, rely=0.45, anchor="center")\n\n        title = str(\n            item.get("title")\n            or definition.get("title", "Page")\n        )\n        caption = title\n        if page_number is not None:\n            caption = f"p. {page_number} · {title}"\n        if done:\n            caption = f"✓ {caption}"\n\n        ctk.CTkLabel(\n            wrapper,\n            text=caption,\n            height=24,\n            font=Fonts.SMALL,\n            text_color=self.DONE if done else self.INK,\n            fg_color=self.GROUP_BG,\n            corner_radius=5,\n            anchor="center",\n        ).grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=8,\n            pady=(4, 0),\n        )\n\n        return wrapper'
ANIMATION_HELPER = '    def _animate_preview_turn(\n        self,\n        direction: int,\n        target_index: int,\n    ) -> None:\n        """Effet rapide de feuille qui pivote autour de la reliure."""\n        if self._preview_body is None:\n            return\n        if bool(getattr(self, "_preview_animating", False)):\n            return\n\n        current = self._preview_spreads[self._preview_index]\n        left_item, right_item, _, _ = current\n        turning_item = (\n            (right_item or left_item)\n            if direction > 0\n            else (left_item or right_item)\n        )\n\n        if turning_item is None:\n            self._preview_index = target_index\n            self._render_preview_current_spread()\n            return\n\n        definition = self._definition_for(\n            str(turning_item.get("type", "autre"))\n        )\n        path = self._thumbnail_path_for_definition(definition)\n        if path is None:\n            self._preview_index = target_index\n            self._render_preview_current_spread()\n            return\n\n        try:\n            from PIL import Image, ImageTk\n\n            source = Image.open(path).convert("RGB")\n            body = self._preview_body\n            body.update_idletasks()\n\n            body_width = max(640, int(body.winfo_width()))\n            body_height = max(460, int(body.winfo_height()))\n            page_height = min(424, max(300, body_height - 70))\n            page_width = max(1, int(round(page_height * 300 / 424)))\n            spine_x = body_width // 2\n            top_y = max(8, (body_height - page_height) // 2 - 8)\n\n            overlay = tk.Label(\n                body,\n                image="",\n                text="",\n                borderwidth=1,\n                relief="solid",\n                background="#FFFFFF",\n                highlightthickness=0,\n            )\n            overlay.lift()\n\n            self._preview_animating = True\n            steps = 7\n            delay = 18\n            widths = [\n                max(8, int(page_width * (1 - step / steps)))\n                for step in range(steps)\n            ]\n            widths += [\n                max(8, int(page_width * (step / steps)))\n                for step in range(1, steps + 1)\n            ]\n\n            def draw(frame_index: int) -> None:\n                if frame_index >= len(widths):\n                    try:\n                        overlay.destroy()\n                    except Exception:\n                        pass\n                    self._preview_animating = False\n                    self._preview_index = target_index\n                    self._render_preview_current_spread()\n                    return\n\n                width = widths[frame_index]\n                resized = source.resize(\n                    (width, page_height),\n                    Image.Resampling.LANCZOS,\n                )\n                photo = ImageTk.PhotoImage(resized)\n                self._preview_turn_photo = photo\n                overlay.configure(image=photo)\n\n                second_half = frame_index >= steps\n                if direction > 0:\n                    x = spine_x if not second_half else spine_x - width\n                else:\n                    x = spine_x - width if not second_half else spine_x\n\n                overlay.place(\n                    x=x,\n                    y=top_y,\n                    width=width,\n                    height=page_height,\n                )\n                overlay.lift()\n                body.after(delay, lambda: draw(frame_index + 1))\n\n            draw(0)\n        except Exception:\n            self._preview_animating = False\n            self._preview_index = target_index\n            self._render_preview_current_spread()'
NEW_PREVIOUS = '    def _show_previous_spread(self) -> None:\n        if (\n            self._preview_mode != "large"\n            or self._preview_index <= 0\n            or bool(getattr(self, "_preview_animating", False))\n        ):\n            return\n        self._animate_preview_turn(-1, self._preview_index - 1)'
NEW_NEXT = '    def _show_next_spread(self) -> None:\n        if (\n            self._preview_mode != "large"\n            or self._preview_index >= len(self._preview_spreads) - 1\n            or bool(getattr(self, "_preview_animating", False))\n        ):\n            return\n        self._animate_preview_turn(1, self._preview_index + 1)'


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
        print("APERCU_GRANDE_VUE_V2_DEJA_APPLIQUE")
        return

    if REQUIRED_MARKER not in original:
        fail(
            "la Grande vue V1 n'est pas détectée. "
            "Par sécurité, aucune modification n'est appliquée."
        )

    candidate = original
    candidate = replace_method(candidate, "_open_preview", NEW_OPEN_PREVIEW)
    candidate = replace_method(candidate, "_create_preview_large_page", NEW_LARGE_PAGE)

    anchor = "    def _show_previous_spread(self) -> None:\n"
    if anchor not in candidate:
        fail("navigation de l'Aperçu introuvable")
    candidate = candidate.replace(
        anchor,
        ANIMATION_HELPER.rstrip() + "\n\n" + anchor,
        1,
    )

    candidate = replace_method(candidate, "_show_previous_spread", NEW_PREVIOUS)
    candidate = replace_method(candidate, "_show_next_spread", NEW_NEXT)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_apercu_grande_vue_v2_{stamp}.py"
    temporary = TARGET.with_suffix(".apercu_grande_vue_v2.tmp")

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

    print("APERCU_GRANDE_VUE_V2_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Outils fixes : centrés horizontalement.")
    print("Pages : image bord à bord, sans marge intérieure.")
    print("Titre et numéro : placés sous la page.")
    print("Navigation : effet rapide de feuille qui tourne.")
    print("Fond validé : inchangé.")
    print("Vue Ensemble : inchangée.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
