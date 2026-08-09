from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"
MARKER = "CENTRE_REGULATION_V1"

NEW_SHOW = r'''    def show(self) -> None:
        self.pages = self._load_project_pages()

        # CENTRE_REGULATION_V1
        # Le ruban permanent assure seul la navigation. Le reste de la page
        # devient le poste de régulation du projet.
        root = ctk.CTkFrame(
            self.parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        navigation = self._create_internal_navigation_ribbon(root)
        navigation.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(5, 3),
        )

        main_workspace = self._create_main_workspace(root)
        main_workspace.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 8),
        )

        root.update_idletasks()
        root.pack(fill="both", expand=True)
        root.lift()
'''

NEW_LOADER = r'''    def _load_regulation_snapshot(self) -> dict:
        """Source commune du Centre et de la future fenêtre Visualisation."""
        snapshot = {
            "items": [],
            "page_types": {},
            "groups": {},
            "updated_at": "",
            "planned_pages": 0,
            "automatic_pages": 0,
            "produced_pages": len(self.pages),
            "validated_pages": sum(
                1
                for page in self.pages
                if "valid" in self._page_state(page).casefold()
            ),
        }

        if self._project_type_key() != "ouvrage_structure":
            return snapshot

        configured = getattr(self.project, "mockup_file", None)
        if configured is not None:
            path = Path(configured)
        else:
            root = getattr(self.project, "root", None)
            if root is None:
                return snapshot
            path = Path(root) / "maquettage" / "premaquette.json"

        if not path.exists():
            return snapshot

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return snapshot

        if not isinstance(data, dict):
            return snapshot

        items = data.get("items", [])
        page_types = data.get("page_types", [])
        groups = data.get("groups", [])

        if not isinstance(items, list):
            items = []
        if not isinstance(page_types, list):
            page_types = []
        if not isinstance(groups, list):
            groups = []

        snapshot["items"] = [
            item for item in items if isinstance(item, dict)
        ]
        snapshot["page_types"] = {
            str(definition.get("type", "")): definition
            for definition in page_types
            if isinstance(definition, dict)
            and str(definition.get("type", ""))
        }
        snapshot["groups"] = {
            str(group.get("id", "")): group
            for group in groups
            if isinstance(group, dict)
            and str(group.get("id", ""))
        }
        snapshot["updated_at"] = str(data.get("updated_at", ""))

        def count_of(item: dict) -> int:
            try:
                return max(1, int(item.get("count", 1) or 1))
            except (TypeError, ValueError):
                return 1

        snapshot["planned_pages"] = sum(
            count_of(item) for item in snapshot["items"]
        )
        snapshot["automatic_pages"] = sum(
            count_of(item)
            for item in snapshot["items"]
            if bool(item.get("automatic_recto_verso", False))
        )

        return snapshot
'''

NEW_MAIN = r'''    def _create_main_workspace(self, parent) -> ctk.CTkFrame:
        """Centre de régulation : synoptique du livre + informations utiles."""
        workspace = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=0, minsize=314)
        workspace.grid_rowconfigure(0, weight=1)

        snapshot = self._load_regulation_snapshot()

        # ======================================================
        # Mur synoptique — base de la future Visualisation
        # ======================================================

        wall = tk.Canvas(
            workspace,
            background=self.WINDOW_BG,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            cursor="arrow",
        )
        wall.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7),
        )
        wall._regulation_bg_photo = None

        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_accueil.png"
        )

        def blend(color: str, amount: float = 0.72) -> str:
            value = str(color).lstrip("#")
            try:
                rgb = [
                    int(value[index:index + 2], 16)
                    for index in (0, 2, 4)
                ]
            except (TypeError, ValueError):
                rgb = [117, 182, 219]
            mixed = [
                int(round(channel + (255 - channel) * amount))
                for channel in rgb
            ]
            return "#{:02X}{:02X}{:02X}".format(*mixed)

        def item_title(item: dict) -> str:
            page_type = str(item.get("type", ""))
            definition = snapshot["page_types"].get(page_type, {})
            return str(
                item.get("title")
                or definition.get("title")
                or page_type.replace("_", " ").title()
                or "Page"
            )

        def item_accent(item: dict) -> str:
            if bool(item.get("automatic_recto_verso", False)):
                return "#AEB5BC"

            group_id = str(item.get("plan_group", ""))
            group = snapshot["groups"].get(group_id, {})
            accent = str(group.get("accent", "") or "")
            if accent.startswith("#") and len(accent) == 7:
                return accent

            page_type = str(item.get("type", ""))
            definition = snapshot["page_types"].get(page_type, {})
            accent = str(definition.get("accent", "") or "")
            if accent.startswith("#") and len(accent) == 7:
                return accent

            return self.MAQUETTAGE

        def make_background(width: int, height: int):
            try:
                from PIL import Image, ImageDraw
            except Exception:
                return None

            if background_path.is_file():
                try:
                    source = Image.open(background_path).convert("RGBA")
                    source_ratio = source.width / source.height
                    target_ratio = width / max(1, height)

                    if target_ratio > source_ratio:
                        rw = width
                        rh = max(height, int(round(width / source_ratio)))
                    else:
                        rh = height
                        rw = max(width, int(round(height * source_ratio)))

                    source = source.resize(
                        (rw, rh),
                        Image.Resampling.LANCZOS,
                    )
                    left = max(0, (rw - width) // 2)
                    top = max(0, (rh - height) // 2)
                    image = source.crop(
                        (left, top, left + width, top + height)
                    )
                    veil = Image.new(
                        "RGBA",
                        (width, height),
                        (255, 255, 255, 108),
                    )
                    image = Image.alpha_composite(image, veil)
                except Exception:
                    image = Image.new(
                        "RGBA",
                        (width, height),
                        (247, 247, 244, 255),
                    )
            else:
                image = Image.new(
                    "RGBA",
                    (width, height),
                    (247, 247, 244, 255),
                )

            draw = ImageDraw.Draw(image)
            line = (72, 92, 112, 38)
            blue = (117, 182, 219, 72)
            teal = (130, 183, 161, 65)
            lilac = (169, 151, 201, 60)

            draw.line(
                (22, height - 22, width - 22, height - 22),
                fill=line,
                width=1,
            )
            for x in (34, width // 2, max(34, width - 34)):
                draw.line(
                    (x - 8, height - 22, x + 8, height - 22),
                    fill=blue,
                    width=1,
                )
                draw.line(
                    (x, height - 30, x, height - 14),
                    fill=blue,
                    width=1,
                )

            cx = width // 2
            by = height - 18
            draw.line(
                (
                    cx - 18, by - 10,
                    cx - 2, by - 7,
                    cx - 2, by + 3,
                    cx - 18, by,
                    cx - 18, by - 10,
                ),
                fill=teal,
                width=1,
            )
            draw.line(
                (
                    cx + 18, by - 10,
                    cx + 2, by - 7,
                    cx + 2, by + 3,
                    cx + 18, by,
                    cx + 18, by - 10,
                ),
                fill=lilac,
                width=1,
            )
            return image

        def draw_wall(_event=None) -> None:
            width = max(1, int(wall.winfo_width()))
            height = max(1, int(wall.winfo_height()))
            if width <= 4 or height <= 4:
                return

            wall.delete("all")

            background = make_background(width, height)
            if background is not None:
                try:
                    from PIL import ImageTk
                    photo = ImageTk.PhotoImage(background)
                    wall._regulation_bg_photo = photo
                    wall.create_image(0, 0, image=photo, anchor="nw")
                except Exception:
                    pass

            wall.create_text(
                22,
                18,
                text="Synoptique du livre",
                fill=self.INK,
                font=(Fonts.FAMILY, 13, "bold"),
                anchor="nw",
            )
            wall.create_text(
                width - 22,
                20,
                text=(
                    f"{snapshot['planned_pages']} pages prévues"
                    if snapshot["planned_pages"]
                    else "Structure non définie"
                ),
                fill=self.TEXT_MUTED,
                font=(Fonts.FAMILY, 9),
                anchor="ne",
            )
            wall.create_text(
                22,
                45,
                text="Vue de régulation · base de la future fenêtre Visualisation",
                fill=self.TEXT_MUTED,
                font=(Fonts.FAMILY, 8),
                anchor="nw",
            )

            items = snapshot["items"]
            if not items:
                wall.create_text(
                    width / 2,
                    max(130, height / 2 - 10),
                    text="Le plan du livre n'est pas encore disponible.",
                    fill=self.INK,
                    font=(Fonts.FAMILY, 12, "bold"),
                    anchor="center",
                )
                wall.create_text(
                    width / 2,
                    max(155, height / 2 + 18),
                    text="Le Maquettage alimentera automatiquement ce synoptique.",
                    fill=self.TEXT_MUTED,
                    font=(Fonts.FAMILY, 9),
                    anchor="center",
                )
                return

            left = 22
            top = 78
            gap_x = 10
            gap_y = 12
            card_w = 132
            card_h = 88
            usable = max(card_w, width - (left * 2))
            columns = max(1, int((usable + gap_x) // (card_w + gap_x)))

            for index, item in enumerate(items):
                row = index // columns
                column = index % columns
                x1 = left + column * (card_w + gap_x)
                y1 = top + row * (card_h + gap_y)
                x2 = x1 + card_w
                y2 = y1 + card_h

                if y2 > height - 38:
                    remaining = len(items) - index
                    wall.create_text(
                        left,
                        min(height - 42, y1 + 10),
                        text=f"… {remaining} élément(s) supplémentaire(s)",
                        fill=self.TEXT_MUTED,
                        font=(Fonts.FAMILY, 9, "italic"),
                        anchor="nw",
                    )
                    break

                accent = item_accent(item)
                soft = blend(accent, 0.78)
                automatic = bool(item.get("automatic_recto_verso", False))
                try:
                    count = max(1, int(item.get("count", 1) or 1))
                except (TypeError, ValueError):
                    count = 1
                title = item_title(item)
                tag = f"regulation_item_{index}"

                wall.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=soft,
                    outline=accent,
                    width=1,
                    stipple="gray25",
                    tags=(tag,),
                )

                page_x1 = x1 + 11
                page_y1 = y1 + 11
                page_x2 = page_x1 + 38
                page_y2 = page_y1 + 54
                wall.create_rectangle(
                    page_x1,
                    page_y1,
                    page_x2,
                    page_y2,
                    fill="#FFFFFF",
                    outline=accent,
                    width=1,
                    tags=(tag,),
                )
                wall.create_line(
                    page_x1 + 7,
                    page_y1 + 10,
                    page_x2 - 7,
                    page_y1 + 10,
                    fill=accent,
                    width=2,
                    tags=(tag,),
                )
                wall.create_line(
                    page_x1 + 7,
                    page_y1 + 18,
                    page_x2 - 9,
                    page_y1 + 18,
                    fill=self.BORDER,
                    width=1,
                    tags=(tag,),
                )
                wall.create_line(
                    page_x1 + 7,
                    page_y1 + 24,
                    page_x2 - 11,
                    page_y1 + 24,
                    fill=self.BORDER,
                    width=1,
                    tags=(tag,),
                )
                wall.create_text(
                    x1 + 59,
                    y1 + 15,
                    text=self._truncate(title, 17),
                    fill=self.INK,
                    font=(Fonts.FAMILY, 9, "bold"),
                    anchor="nw",
                    tags=(tag,),
                )
                wall.create_text(
                    x1 + 59,
                    y1 + 38,
                    text=("Blanc automatique" if automatic else "Maquette"),
                    fill=accent if not automatic else self.TEXT_MUTED,
                    font=(Fonts.FAMILY, 8),
                    anchor="nw",
                    tags=(tag,),
                )
                wall.create_text(
                    x1 + 59,
                    y1 + 60,
                    text=(f"×{count}" if count > 1 else "1 page"),
                    fill=self.TEXT_MUTED,
                    font=(Fonts.FAMILY, 8),
                    anchor="nw",
                    tags=(tag,),
                )

                if not automatic:
                    wall.tag_bind(
                        tag,
                        "<Button-1>",
                        lambda _evt: self._open_mockup(),
                    )
                    wall.tag_bind(
                        tag,
                        "<Enter>",
                        lambda _evt: wall.configure(cursor="hand2"),
                    )
                    wall.tag_bind(
                        tag,
                        "<Leave>",
                        lambda _evt: wall.configure(cursor="arrow"),
                    )

        wall.bind("<Configure>", draw_wall, add="+")
        wall.after_idle(draw_wall)

        # ======================================================
        # Tableau de régulation
        # ======================================================

        side = ctk.CTkFrame(
            workspace,
            width=314,
            fg_color=self.CARD_BG,
            corner_radius=9,
            border_width=1,
            border_color=self.BORDER,
        )
        side.grid(row=0, column=1, sticky="nsew")
        side.grid_propagate(False)
        side.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            side,
            text="Régulation",
            font=(Fonts.FAMILY, 12, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=14,
            pady=(13, 2),
        )
        ctk.CTkLabel(
            side,
            text="Informations utiles au pilotage du livre.",
            font=(Fonts.FAMILY, 8),
            text_color=self.TEXT_MUTED,
            anchor="w",
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 10),
        )

        def metric(row: int, label: str, value: str, color: str) -> None:
            frame = ctk.CTkFrame(
                side,
                height=39,
                fg_color=blend(color, 0.87),
                corner_radius=7,
                border_width=1,
                border_color=blend(color, 0.50),
            )
            frame.grid(
                row=row,
                column=0,
                sticky="ew",
                padx=12,
                pady=(0, 5),
            )
            frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                frame,
                text=label,
                font=(Fonts.FAMILY, 8),
                text_color=self.TEXT_MUTED,
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=(10, 4), pady=7)
            ctk.CTkLabel(
                frame,
                text=value,
                font=(Fonts.FAMILY, 10, "bold"),
                text_color=color,
            ).grid(row=0, column=1, sticky="e", padx=(4, 10), pady=7)

        metric(2, "Pages prévues", str(snapshot["planned_pages"]), self.MAQUETTAGE)
        metric(3, "Pages automatiques", str(snapshot["automatic_pages"]), self.ATELIER)
        metric(4, "Pages produites", str(snapshot["produced_pages"]), self.CONCEPTION)
        metric(5, "Pages validées", str(snapshot["validated_pages"]), self.VERIFICATION)

        ctk.CTkLabel(
            side,
            text="À traiter",
            font=(Fonts.FAMILY, 10, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=6,
            column=0,
            sticky="ew",
            padx=14,
            pady=(12, 5),
        )

        work_pages = max(0, snapshot["planned_pages"] - snapshot["automatic_pages"])
        remaining_to_produce = max(0, work_pages - snapshot["produced_pages"])
        alerts = []

        if not snapshot["items"]:
            alerts.append(("Plan du livre", "Le Maquettage doit encore définir la structure."))
        elif remaining_to_produce:
            alerts.append(("Production", f"{remaining_to_produce} page(s) restent à produire."))

        if snapshot["produced_pages"] > snapshot["validated_pages"]:
            alerts.append(
                (
                    "Validation",
                    f"{snapshot['produced_pages'] - snapshot['validated_pages']} page(s) produite(s) non validée(s).",
                )
            )

        if not alerts:
            alerts.append(("Aucune alerte", "Le projet ne demande pas d'intervention immédiate."))

        for offset, (title, text) in enumerate(alerts[:3]):
            alert = ctk.CTkFrame(
                side,
                fg_color="#F7F8F6",
                corner_radius=7,
                border_width=1,
                border_color=self.BORDER,
            )
            alert.grid(
                row=7 + offset,
                column=0,
                sticky="ew",
                padx=12,
                pady=(0, 5),
            )
            alert.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                alert,
                text=title,
                font=(Fonts.FAMILY, 8, "bold"),
                text_color=self.INK,
                anchor="w",
            ).grid(row=0, column=0, sticky="ew", padx=9, pady=(6, 0))
            ctk.CTkLabel(
                alert,
                text=text,
                font=(Fonts.FAMILY, 8),
                text_color=self.TEXT_MUTED,
                anchor="w",
                justify="left",
                wraplength=260,
            ).grid(row=1, column=0, sticky="ew", padx=9, pady=(1, 7))

        if callable(self.on_cleanup):
            ctk.CTkButton(
                side,
                text="Nettoyage du projet",
                height=30,
                corner_radius=6,
                fg_color="transparent",
                hover_color=Colors.BUTTON_HOVER,
                text_color=self.INK,
                border_width=1,
                border_color=self.BORDER,
                font=(Fonts.FAMILY, 8),
                command=self.on_cleanup,
            ).grid(
                row=11,
                column=0,
                sticky="ew",
                padx=12,
                pady=(12, 10),
            )

        return workspace
'''


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


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


def replace_method(source: str, name: str, replacement: str) -> str:
    old = get_method(source, name)
    return source.replace(old, replacement.rstrip() + "\n\n", 1)


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("CENTRE_REGULATION_V1_DEJA_APPLIQUE")
        return

    if "def _create_internal_navigation_ribbon" not in original:
        fail("ruban permanent introuvable")
    if "def _create_main_workspace" not in original:
        fail("espace principal du Centre introuvable")

    candidate = replace_method(original, "show", NEW_SHOW)

    old_main = get_method(candidate, "_create_main_workspace")
    candidate = candidate.replace(
        old_main,
        NEW_LOADER.rstrip() + "\n\n" + NEW_MAIN.rstrip() + "\n\n",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_centre_regulation_{stamp}.py"
    temp = TARGET.with_suffix(".centre_regulation.tmp")

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

    print("CENTRE_REGULATION_V1_OK")
    print("Le ruban permanent validé est inchangé.")
    print("Les anciens raccourcis de bureaux ne sont plus affichés sous le ruban.")
    print("Le synoptique lit directement le Maquettage.")
    print("Le panneau de droite regroupe les informations utiles à la régulation.")
    print("Cette source servira ensuite à la fenêtre Visualisation.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
