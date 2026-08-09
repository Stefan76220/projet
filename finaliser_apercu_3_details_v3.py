from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
REQUIRED_MARKER = "APERCU_COMMANDES_EPUREES_SANS_FLASH_V2"
NEW_MARKER = "APERCU_FINITION_VISUELLE_V3"

EXPECTED = {'_open_preview': 'e3a6e690751cd12fc4ed0f6729276ce21280cb58da93cc996dc8793e0dae2160', '_render_preview_current_spread': 'd67a4240bab0dd8401e47748162ffe6fb43479f22d3a1fcf6bae873db00c094b', '_update_preview_navigation': '5dc6a2839ca34e7ac85e0cf68039ebcfd4cead30080d5d026ae519cf6dfccaf1'}

NEW_OPEN = '    def _open_preview(self) -> None:\n        if self._preview_window is not None:\n            try:\n                if self._preview_window.winfo_exists():\n                    self._preview_window.focus_force()\n                    self._preview_window.lift()\n                    return\n            except Exception:\n                self._preview_window = None\n\n        window = ctk.CTkToplevel(self.parent)\n        self._preview_window = window\n        window.title("Projet envisagé")\n\n        # APERCU_GRANDE_VUE_V3\n        # APERCU_MAQUETTAGE_GRANDE_VUE_SEULE_V1\n        # APERCU_CADRAGE_VERTICAL_CENTRE_V1\n        # APERCU_FOND_CONTINU_CENTRAGE_V1\n        # APERCU_OUTILS_RESPIRATION_V1\n        # APERCU_COMMANDES_EPUREES_SANS_FLASH_V2\n        # APERCU_FINITION_VISUELLE_V3\n        # APERCU_FENETRE_CENTREE_V1\n        preview_width = 840\n        preview_height = 650\n        window.minsize(740, 560)\n        window.update_idletasks()\n\n        screen_width = int(window.winfo_screenwidth())\n        screen_height = int(window.winfo_screenheight())\n        pos_x = max(0, (screen_width - preview_width) // 2)\n        pos_y = max(0, (screen_height - preview_height) // 2)\n\n        window.geometry(\n            f"{preview_width}x{preview_height}+{pos_x}+{pos_y}"\n        )\n        window.configure(fg_color=self.WINDOW_BG)\n        window.protocol("WM_DELETE_WINDOW", self._close_preview)\n        window.grid_columnconfigure(0, weight=1)\n        window.grid_rowconfigure(2, weight=1)\n        window.bind("<Left>", lambda _event: self._show_previous_spread())\n        window.bind("<Right>", lambda _event: self._show_next_spread())\n\n        self._preview_animating = False\n        self._preview_turn_photo = None\n        self._preview_turn_overlay = None\n        self._preview_turn_shadow = None\n        self._preview_static_widgets: list[tk.Widget] = []\n        self._preview_static_canvas_items: list[int] = []\n\n        header = ctk.CTkFrame(window, fg_color="transparent", height=32)\n        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 4))\n        header.grid_columnconfigure(0, weight=1)\n        header.grid_propagate(False)\n\n        ctk.CTkLabel(\n            header,\n            text="Projet envisagé",\n            font=Fonts.H2,\n            text_color=self.INK,\n        ).grid(row=0, column=0, sticky="w")\n\n        ctk.CTkLabel(\n            header,\n            text=self._preview_summary_text(),\n            font=Fonts.SMALL,\n            text_color=self.TEXT_MUTED,\n        ).grid(row=0, column=1, sticky="e")\n\n        # Les trois commandes universelles sont posées directement\n        # sur le décor PageMaître, sans groupe ni bandeau coloré.\n        ribbon = self._create_preview_background_canvas(\n            window,\n            fixed_height=66,\n        )\n        ribbon.configure(highlightthickness=0)\n        ribbon.grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=12,\n            pady=(0, 6),\n        )\n        ribbon.grid_propagate(False)\n\n        def preview_icon_button(\n            icon: str,\n            command,\n            x_offset: int,\n            *,\n            accent: str | None = None,\n            tooltip: str,\n        ) -> ctk.CTkButton:\n            text_color = accent or self.INK\n            border = self._mix_color_with_white(text_color, 0.55)\n            hover = self._mix_color_with_white(text_color, 0.88)\n            button = ctk.CTkButton(\n                ribbon,\n                text=icon,\n                width=66,\n                height=39,\n                corner_radius=5,\n                fg_color=self.GROUP_BG,\n                hover_color=hover,\n                text_color=text_color,\n                border_width=1,\n                border_color=border,\n                font=(Fonts.FAMILY, 14, "bold"),\n                command=command,\n            )\n            button.place(\n                relx=0.5,\n                rely=0.5,\n                x=x_offset,\n                anchor="center",\n            )\n            self._attach_tooltip(button, tooltip)\n            return button\n\n        self._preview_previous_button = preview_icon_button(\n            "◀",\n            self._show_previous_spread,\n            -70,\n            tooltip="Précédent",\n        )\n        self._preview_next_button = preview_icon_button(\n            "▶",\n            self._show_next_spread,\n            0,\n            tooltip="Suivant",\n        )\n        preview_icon_button(\n            "×",\n            self._close_preview,\n            70,\n            accent=self.CORAL,\n            tooltip="Fermer",\n        )\n\n        # Une seule surface décorée reçoit directement les pages et leurs noms.\n        # Aucun panneau intermédiaire n\'est visible sous le livre.\n        self._preview_body = self._create_preview_background_canvas(window)\n        self._preview_body.configure(highlightthickness=0)\n        self._preview_body.grid(\n            row=2,\n            column=0,\n            sticky="nsew",\n            padx=12,\n            pady=(0, 5),\n        )\n\n        # Aucune barre d\'état opaque : les informations de position sont\n        # dessinées directement sur le décor général, sous le livre.\n        self._preview_nav = None\n        self._preview_position_label = None\n\n        self._preview_spreads = self._build_preview_spreads(\n            list(self._items())\n        )\n        self._preview_index = 0\n        self._preview_mode = "large"\n        self._preview_large_button = None\n        self._preview_overview_button = None\n        # Laisse Tk calculer la largeur réelle du Canvas avant de placer\n        # la couverture. Cela évite qu\'elle utilise la largeur de secours\n        # de 640 px et apparaisse décalée vers la gauche au premier affichage.\n        window.update_idletasks()\n        window.after(40, self._render_preview_current_spread)\n        window.after(100, window.focus_force)\n\n'
NEW_RENDER = '    def _render_preview_current_spread(self) -> None:\n        body = self._preview_body\n        if body is None:\n            return\n\n        body.update_idletasks()\n        body_width = max(640, int(body.winfo_width()))\n        body_height = max(460, int(body.winfo_height()))\n\n        old_widgets = list(\n            getattr(self, "_preview_static_widgets", [])\n        )\n        old_items = list(\n            getattr(self, "_preview_static_canvas_items", [])\n        )\n        new_widgets: list[tk.Widget] = []\n        new_items: list[int] = []\n\n        def caption_for(\n            item: dict[str, Any],\n            number: int | None,\n        ) -> tuple[str, str]:\n            definition = self._definition_for(\n                str(item.get("type", "autre"))\n            )\n            title = str(\n                item.get("title")\n                or definition.get("title", "Page")\n            )\n            caption = title\n            if number is not None:\n                caption = f"p. {number} · {title}"\n            done = bool(item.get("done", False))\n            if done:\n                caption = f"✓ {caption}"\n            return caption, self.DONE if done else self.INK\n\n        if not self._preview_spreads:\n            new_items.append(\n                body.create_text(\n                    body_width // 2,\n                    body_height // 2,\n                    text="Aucune page.",\n                    fill=self.TEXT_LIGHT,\n                    font=Fonts.NORMAL,\n                    anchor="center",\n                )\n            )\n        else:\n            self._preview_index = max(\n                0,\n                min(self._preview_index, len(self._preview_spreads) - 1),\n            )\n            left_item, right_item, left_number, right_number = (\n                self._preview_spreads[self._preview_index]\n            )\n\n            visible_pages = [\n                (left_item, left_number),\n                (right_item, right_number),\n            ]\n            visible_pages = [\n                (item, number)\n                for item, number in visible_pages\n                if item is not None\n            ]\n\n            page_width = 300\n            page_height = 424\n            caption_gap = 19\n            block_height = page_height + 38\n            top_y = max(4, (body_height - block_height) // 2)\n\n            if len(visible_pages) == 1:\n                item, number = visible_pages[0]\n                page = self._create_preview_large_page(\n                    body,\n                    item,\n                    number,\n                )\n                x = (body_width - page_width) // 2\n                new_widgets.append(page)\n                new_items.append(\n                    body.create_window(\n                        x,\n                        top_y,\n                        window=page,\n                        anchor="nw",\n                        width=page_width,\n                        height=page_height,\n                    )\n                )\n\n                caption, color = caption_for(item, number)\n                new_items.append(\n                    body.create_text(\n                        body_width // 2,\n                        top_y + page_height + caption_gap,\n                        text=caption,\n                        fill=color,\n                        font=Fonts.SMALL,\n                        anchor="center",\n                        width=page_width,\n                    )\n                )\n            else:\n                gap = 14\n                total_width = page_width * 2 + gap\n                left_x = (body_width - total_width) // 2\n                right_x = left_x + page_width + gap\n\n                for item, number, x in (\n                    (left_item, left_number, left_x),\n                    (right_item, right_number, right_x),\n                ):\n                    if item is None:\n                        continue\n\n                    page = self._create_preview_large_page(\n                        body,\n                        item,\n                        number,\n                    )\n                    new_widgets.append(page)\n                    new_items.append(\n                        body.create_window(\n                            x,\n                            top_y,\n                            window=page,\n                            anchor="nw",\n                            width=page_width,\n                            height=page_height,\n                        )\n                    )\n\n                    caption, color = caption_for(item, number)\n                    new_items.append(\n                        body.create_text(\n                            x + page_width // 2,\n                            top_y + page_height + caption_gap,\n                            text=caption,\n                            fill=color,\n                            font=Fonts.SMALL,\n                            anchor="center",\n                            width=page_width,\n                        )\n                    )\n\n        # Position dans le livre : directement sur le décor général,\n        # sans bandeau ni fond opaque.\n        if self._preview_spreads:\n            position = self._preview_spread_title(\n                left_item,\n                right_item,\n                left_number,\n                right_number,\n            )\n            new_items.append(\n                body.create_text(\n                    body_width // 2,\n                    max(12, body_height - 12),\n                    text=(\n                        f"{position}   ·   "\n                        f"{self._preview_index + 1} / "\n                        f"{len(self._preview_spreads)}"\n                    ),\n                    fill=self.INK,\n                    font=Fonts.SMALL,\n                    anchor="s",\n                )\n            )\n\n        # Double tampon : le nouvel état est entièrement créé avant que\n        # l\'ancien disparaisse. Lors d\'une rotation, la feuille animée reste\n        # au-dessus pendant cette bascule, ce qui supprime le flash blanc.\n        body.update_idletasks()\n\n        for widget in old_widgets:\n            try:\n                widget.destroy()\n            except Exception:\n                pass\n        for item_id in old_items:\n            try:\n                body.delete(item_id)\n            except Exception:\n                pass\n\n        self._preview_static_widgets = new_widgets\n        self._preview_static_canvas_items = new_items\n        self._update_preview_navigation()\n\n'
NEW_UPDATE = '    def _update_preview_navigation(self) -> None:\n        total = len(self._preview_spreads)\n\n        if self._preview_previous_button is not None:\n            self._preview_previous_button.configure(\n                state="normal" if self._preview_index > 0 else "disabled"\n            )\n\n        if self._preview_next_button is not None:\n            self._preview_next_button.configure(\n                state=(\n                    "normal"\n                    if self._preview_index < total - 1\n                    else "disabled"\n                )\n            )\n'


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


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("APERCU_FINITION_VISUELLE_DEJA_APPLIQUEE")
        return

    if REQUIRED_MARKER not in original:
        fail("le correctif Aperçu V2 n'est pas détecté")

    for name, expected in EXPECTED.items():
        if digest(get_method(original, name)) != expected:
            fail(
                f"la méthode {name} ne correspond pas à la version V2 "
                "attendue. Aucune modification appliquée."
            )

    candidate = original
    for name, block in (
        ("_open_preview", NEW_OPEN),
        ("_render_preview_current_spread", NEW_RENDER),
        ("_update_preview_navigation", NEW_UPDATE),
    ):
        candidate = replace_method(candidate, name, block)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_finition_apercu_v3_{stamp}.py"
    temp = TARGET.with_suffix(".finition_apercu.tmp")

    try:
        temp.write_text(candidate, encoding="utf-8")
        py_compile.compile(str(temp), doraise=True)
        shutil.copy2(TARGET, backup)
        temp.replace(TARGET)
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass
        if backup.exists():
            shutil.copy2(backup, TARGET)
        fail(f"installation annulée automatiquement : {exc}")

    print("APERCU_FINITION_VISUELLE_V3_OK")
    print("Bandeau outils : hauteur 66 px.")
    print("Première page : rendu après calcul de la largeur réelle.")
    print("Bandeau blanc inférieur : supprimé.")
    print("Position dans le livre : texte directement sur le décor.")
    print("Noms de pages : restent directement sur le décor.")
    print("Rotation sans flash V2 : conservée.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
