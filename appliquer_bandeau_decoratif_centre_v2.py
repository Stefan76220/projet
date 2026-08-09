from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

OLD_MARKER = "BANDEAU_NAVIGATION_PERMANENT_V1"
NEW_MARKER = "Bandeau décoratif permanent de navigation PageMaître"
NEW_METHOD = '    def _create_internal_navigation_ribbon(\n        self,\n        parent,\n    ) -> ctk.CTkFrame:\n        """Bandeau décoratif permanent de navigation PageMaître.\n\n        Même logique de navigation que la V1, mais sans aspect "barre d\'outils" :\n        les accès sont posés directement sur le décor, avec une iconographie\n        homogène et une frise éditoriale rectiligne discrète.\n        """\n        ribbon = ctk.CTkFrame(\n            parent,\n            height=88,\n            fg_color=self.RIBBON_BG,\n            corner_radius=10,\n            border_width=1,\n            border_color=self.BORDER,\n        )\n        ribbon.grid_propagate(False)\n        ribbon.grid_columnconfigure(0, weight=0, minsize=230)\n        ribbon.grid_columnconfigure(1, weight=1)\n        ribbon.grid_columnconfigure(2, weight=0, minsize=92)\n        ribbon.grid_rowconfigure(0, weight=1)\n\n        # ======================================================\n        # Fond général + décor éditorial discret\n        # ======================================================\n\n        decor = tk.Canvas(\n            ribbon,\n            background=self.RIBBON_BG,\n            borderwidth=0,\n            highlightthickness=0,\n            takefocus=False,\n        )\n        decor.place(x=0, y=0, relwidth=1, relheight=1)\n\n        background_path = (\n            Path(__file__).resolve().parents[3]\n            / "assets"\n            / "interface"\n            / "backgrounds"\n            / "editorial_bg_soft.png"\n        )\n\n        source = None\n        try:\n            from PIL import Image, ImageTk\n\n            if background_path.is_file():\n                source = Image.open(background_path).convert("RGB")\n        except Exception:\n            source = None\n\n        ribbon._navigation_bg_source = source\n        ribbon._navigation_bg_photo = None\n\n        def draw_decor(_event=None) -> None:\n            try:\n                width = max(1, int(ribbon.winfo_width()))\n                height = max(1, int(ribbon.winfo_height()))\n                if width <= 2 or height <= 2:\n                    return\n\n                decor.configure(width=width, height=height)\n                decor.delete("all")\n\n                # Fond général PageMaître.\n                if source is not None:\n                    from PIL import Image, ImageTk\n\n                    source_ratio = source.width / source.height\n                    target_ratio = width / height\n\n                    if target_ratio > source_ratio:\n                        resize_width = width\n                        resize_height = max(\n                            height,\n                            int(round(width / source_ratio)),\n                        )\n                    else:\n                        resize_height = height\n                        resize_width = max(\n                            width,\n                            int(round(height * source_ratio)),\n                        )\n\n                    resized = source.resize(\n                        (resize_width, resize_height),\n                        Image.Resampling.LANCZOS,\n                    )\n                    left = max(0, (resize_width - width) // 2)\n                    top = max(0, (resize_height - height) // 2)\n                    cropped = resized.crop(\n                        (left, top, left + width, top + height)\n                    )\n\n                    photo = ImageTk.PhotoImage(cropped)\n                    ribbon._navigation_bg_photo = photo\n                    decor.create_image(0, 0, image=photo, anchor="nw")\n\n                # Références discrètes à l\'édition :\n                # ligne de composition, repères, mini-couleurs, livre ouvert.\n                y = height - 12\n                ink_soft = "#B8C7D4"\n                teal_soft = "#A9CEC6"\n                lilac_soft = "#C8BDD9"\n                coral_soft = "#E7B0A3"\n\n                decor.create_line(\n                    26, y,\n                    max(26, width - 26), y,\n                    fill=ink_soft,\n                    width=1,\n                )\n\n                # Repères de coupe / composition.\n                for x in (34, width // 2, max(34, width - 34)):\n                    decor.create_line(\n                        x - 7, y, x + 7, y,\n                        fill=ink_soft,\n                        width=1,\n                    )\n                    decor.create_line(\n                        x, y - 7, x, y + 7,\n                        fill=ink_soft,\n                        width=1,\n                    )\n                    decor.create_oval(\n                        x - 2, y - 2, x + 2, y + 2,\n                        outline=ink_soft,\n                        width=1,\n                    )\n\n                # Mini gamme chromatique à gauche.\n                swatch_x = 170\n                for color in (\n                    self.CELADON,\n                    self.SKY,\n                    self.LILAC,\n                    self.CORAL,\n                ):\n                    decor.create_rectangle(\n                        swatch_x, y - 3,\n                        swatch_x + 10, y + 3,\n                        outline=color,\n                        fill="",\n                        width=1,\n                    )\n                    swatch_x += 15\n\n                # Livre ouvert minimal au centre.\n                book_x = width // 2\n                book_y = y - 2\n                decor.create_line(\n                    book_x - 16, book_y - 7,\n                    book_x - 2, book_y - 5,\n                    book_x - 2, book_y + 5,\n                    book_x - 16, book_y + 3,\n                    book_x - 16, book_y - 7,\n                    fill=teal_soft,\n                    width=1,\n                )\n                decor.create_line(\n                    book_x + 16, book_y - 7,\n                    book_x + 2, book_y - 5,\n                    book_x + 2, book_y + 5,\n                    book_x + 16, book_y + 3,\n                    book_x + 16, book_y - 7,\n                    fill=lilac_soft,\n                    width=1,\n                )\n                decor.create_line(\n                    book_x, book_y - 5,\n                    book_x, book_y + 6,\n                    fill=ink_soft,\n                    width=1,\n                )\n\n                # Petites ponctuations de mise en page à droite.\n                dot_x = max(0, width - 214)\n                for row in range(2):\n                    for col in range(7):\n                        color = coral_soft if (row + col) % 3 == 0 else ink_soft\n                        x = dot_x + (col * 8)\n                        dot_y = y - 5 + (row * 5)\n                        decor.create_oval(\n                            x, dot_y, x + 2, dot_y + 2,\n                            fill=color,\n                            outline="",\n                        )\n            except Exception:\n                pass\n\n        ribbon.bind("<Configure>", draw_decor, add="+")\n        ribbon.after_idle(draw_decor)\n        decor.lower()\n\n        # ======================================================\n        # Conteneurs de navigation\n        # ======================================================\n\n        left = ctk.CTkFrame(\n            ribbon,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        left.grid(\n            row=0,\n            column=0,\n            sticky="nsw",\n            padx=(10, 2),\n            pady=(5, 15),\n        )\n\n        centre = ctk.CTkFrame(\n            ribbon,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        centre.grid(\n            row=0,\n            column=1,\n            sticky="nsew",\n            padx=2,\n            pady=(5, 15),\n        )\n\n        right = ctk.CTkFrame(\n            ribbon,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        right.grid(\n            row=0,\n            column=2,\n            sticky="nse",\n            padx=(2, 10),\n            pady=(5, 15),\n        )\n\n        # Fines séparations uniquement structurelles.\n        ctk.CTkFrame(\n            ribbon,\n            width=1,\n            fg_color="#D9E0E5",\n            corner_radius=0,\n        ).place(relx=0, x=226, y=13, height=48)\n\n        ctk.CTkFrame(\n            ribbon,\n            width=1,\n            fg_color="#D9E0E5",\n            corner_radius=0,\n        ).place(relx=1, x=-94, y=13, height=48)\n\n        # ======================================================\n        # Élément de navigation décoratif\n        # ======================================================\n\n        def navigation_item(\n            host,\n            *,\n            icon: str,\n            label: str,\n            color: str,\n            command=None,\n            active: bool = False,\n            enabled: bool = True,\n            width: int = 88,\n        ) -> ctk.CTkFrame:\n            """Accès sans apparence de bouton : icône, nom, trait d\'état."""\n            clickable = enabled and callable(command)\n            item_color = color if (enabled or active) else self.TEXT_LIGHT\n\n            frame = ctk.CTkFrame(\n                host,\n                width=width,\n                height=55,\n                fg_color="transparent",\n                corner_radius=7,\n            )\n            frame.pack_propagate(False)\n\n            icon_label = ctk.CTkLabel(\n                frame,\n                text=icon,\n                height=27,\n                font=(Fonts.FAMILY, 20, "normal"),\n                text_color=item_color,\n            )\n            icon_label.pack(fill="x", pady=(1, 0))\n\n            text_label = ctk.CTkLabel(\n                frame,\n                text=label,\n                height=20,\n                font=(\n                    Fonts.FAMILY,\n                    9,\n                    "bold" if active else "normal",\n                ),\n                text_color=(\n                    self.INK\n                    if active\n                    else item_color\n                ),\n            )\n            text_label.pack(fill="x", pady=(0, 1))\n\n            underline = ctk.CTkFrame(\n                frame,\n                width=28 if active else 4,\n                height=2,\n                fg_color=item_color,\n                corner_radius=1,\n            )\n            underline.pack(pady=(0, 1))\n\n            if clickable:\n                def activate(_event=None) -> None:\n                    command()\n\n                def enter(_event=None) -> None:\n                    frame.configure(fg_color="#F7F9FA")\n\n                def leave(_event=None) -> None:\n                    frame.configure(fg_color="transparent")\n\n                for widget in (\n                    frame,\n                    icon_label,\n                    text_label,\n                    underline,\n                ):\n                    widget.bind("<Button-1>", activate)\n                    widget.bind("<Enter>", enter)\n                    widget.bind("<Leave>", leave)\n\n            return frame\n\n        # ======================================================\n        # Gauche : accès permanents\n        # ======================================================\n\n        navigation_item(\n            left,\n            icon="◉",\n            label="Visualisation",\n            color=self.LILAC,\n            enabled=False,\n            width=104,\n        ).pack(side="left", padx=(0, 2))\n\n        navigation_item(\n            left,\n            icon="♧",\n            label="Suivi du livre",\n            color=self.CELADON,\n            enabled=False,\n            width=106,\n        ).pack(side="left")\n\n        # ======================================================\n        # Centre : parcours complet\n        # Centre possède maintenant son icône, exactement comme les autres.\n        # ======================================================\n\n        flow = ctk.CTkFrame(\n            centre,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        flow.pack(expand=True)\n\n        steps = (\n            (\n                "⌂",\n                "Centre",\n                self.NAVY,\n                None,\n                True,\n                True,\n                70,\n            ),\n            (\n                "✎",\n                "Maquettage",\n                self.MAQUETTAGE,\n                self._open_mockup,\n                False,\n                True,\n                88,\n            ),\n            (\n                "⚒",\n                "Atelier",\n                self.ATELIER,\n                self._open_model_workshop,\n                False,\n                True,\n                72,\n            ),\n            (\n                "✒",\n                "Conception",\n                self.CONCEPTION,\n                self._open_atelier,\n                False,\n                True,\n                88,\n            ),\n            (\n                "▦",\n                "Assemblage",\n                self.ASSEMBLAGE,\n                None,\n                False,\n                False,\n                88,\n            ),\n            (\n                "✓",\n                "Vérification",\n                self.VERIFICATION,\n                None,\n                False,\n                False,\n                90,\n            ),\n            (\n                "⚑",\n                "Finalisation",\n                self.FINALISATION,\n                None,\n                False,\n                False,\n                86,\n            ),\n        )\n\n        for index, (\n            icon,\n            title,\n            color,\n            command,\n            active,\n            enabled,\n            width,\n        ) in enumerate(steps):\n            navigation_item(\n                flow,\n                icon=icon,\n                label=title,\n                color=color,\n                command=command,\n                active=active,\n                enabled=enabled,\n                width=width,\n            ).pack(\n                side="left",\n                padx=(0 if index == 0 else 1, 0),\n            )\n\n        # ======================================================\n        # Droite : fermer, traité comme les autres accès\n        # ======================================================\n\n        navigation_item(\n            right,\n            icon="×",\n            label="Fermer",\n            color=self.CORAL,\n            command=self._return_home,\n            enabled=True,\n            width=78,\n        ).pack()\n\n        return ribbon\n'


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def get_method(source: str, name: str) -> str:
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

    return "".join(lines[start:end])


def replace_method(
    source: str,
    name: str,
    replacement: str,
) -> str:
    old = get_method(source, name)
    return source.replace(
        old,
        replacement.rstrip() + "\n\n",
        1,
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("BANDEAU_DECORATIF_V2_DEJA_APPLIQUE")
        return

    if OLD_MARKER not in original:
        fail(
            "la V1 du bandeau n'est pas détectée dans document_view.py"
        )

    if "def _create_internal_navigation_ribbon" not in original:
        fail("bandeau de navigation V1 introuvable")

    candidate = replace_method(
        original,
        "_create_internal_navigation_ribbon",
        NEW_METHOD,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la nouvelle version ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_bandeau_decoratif_v2_{stamp}.py"
    )
    temp = TARGET.with_suffix(".bandeau_decoratif.tmp")

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

        fail(
            f"installation annulée automatiquement : {exc}"
        )

    print("BANDEAU_DECORATIF_V2_OK")
    print("Centre a maintenant son icône, au même niveau que tous les autres.")
    print("Les cadres de boutons ont disparu.")
    print("Le fond PageMaître est conservé.")
    print("Une frise éditoriale rectiligne et discrète est ajoutée.")
    print("La navigation et les fonctions existantes sont conservées.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
