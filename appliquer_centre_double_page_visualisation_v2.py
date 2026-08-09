from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

MARKER_REQUIRED = "CENTRE_REGULATION_V1"
MARKER_NEW = "CENTRE_VISUALISATION_DOUBLE_PAGE_V2"

NEW_METHOD = r"""    def _create_main_workspace(self, parent) -> ctk.CTkFrame:
        # CENTRE_VISUALISATION_DOUBLE_PAGE_V2
        workspace = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=0, minsize=314)
        workspace.grid_rowconfigure(0, weight=1)

        snapshot = self._load_regulation_snapshot()

        wall_shell = ctk.CTkFrame(
            workspace,
            fg_color="transparent",
            corner_radius=0,
        )
        wall_shell.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7),
        )
        wall_shell.grid_columnconfigure(0, weight=1)
        wall_shell.grid_rowconfigure(0, weight=1)

        wall = tk.Canvas(
            wall_shell,
            background=self.WINDOW_BG,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            cursor="arrow",
        )
        wall.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(
            wall_shell,
            orientation="vertical",
            command=wall.yview,
            width=11,
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(3, 0),
        )
        wall.configure(yscrollcommand=scrollbar.set)

        wall._regulation_bg_photo = None

        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_accueil.png"
        )

        def blend(color: str, amount: float = 0.72) -> str:
            color = str(color or "").lstrip("#")
            try:
                rgb = [
                    int(color[index:index + 2], 16)
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

            group_id = str(
                item.get("plan_group")
                or item.get("group_id")
                or ""
            )
            group = snapshot["groups"].get(group_id, {})
            accent = str(
                group.get("accent")
                or group.get("color")
                or ""
            )
            if accent.startswith("#") and len(accent) == 7:
                return accent

            page_type = str(item.get("type", ""))
            definition = snapshot["page_types"].get(page_type, {})
            accent = str(
                definition.get("accent")
                or definition.get("color")
                or ""
            )
            if accent.startswith("#") and len(accent) == 7:
                return accent

            if page_type in {"couverture", "deuxieme_couverture"}:
                return "#E88972"
            if page_type in {"quatrieme", "troisieme_couverture"}:
                return "#7DB99D"

            return self.MAQUETTAGE

        def expand_items() -> list[dict]:
            expanded: list[dict] = []

            for source_index, item in enumerate(snapshot["items"]):
                try:
                    count = max(1, int(item.get("count", 1) or 1))
                except (TypeError, ValueError):
                    count = 1

                for occurrence in range(count):
                    clone = dict(item)
                    clone["_source_index"] = source_index
                    clone["_occurrence"] = occurrence + 1
                    clone["_occurrence_count"] = count
                    expanded.append(clone)

            return expanded

        physical_pages = expand_items()

        def page_status(item: dict) -> tuple[str, str]:
            if bool(item.get("automatic_recto_verso", False)):
                return "BLANC AUTO", "#87919A"
            return "MAQUETTAGE", item_accent(item)

        def make_background(width: int, height: int):
            try:
                from PIL import Image, ImageDraw
            except Exception:
                return None

            width = max(1, int(width))
            height = max(1, int(height))

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
                        (255, 255, 255, 112),
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
            line = (72, 92, 112, 34)
            blue = (117, 182, 219, 68)
            teal = (130, 183, 161, 58)

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
                    fill=teal,
                    width=1,
                )

            return image

        def draw_page(
            x: float,
            y: float,
            item: dict,
            *,
            page_side: str,
            page_number: int | None,
            scale: float = 1.0,
        ) -> tuple[float, float]:
            page_w = 101 * scale
            page_h = 143 * scale

            accent = item_accent(item)
            soft = blend(accent, 0.89)
            status_text, status_color = page_status(item)

            tag = (
                f"visual_page_"
                f"{item.get('_source_index', 0)}_"
                f"{item.get('_occurrence', 1)}"
            )

            wall.create_rectangle(
                x + 4,
                y + 4,
                x + page_w + 4,
                y + page_h + 4,
                fill="#D9DCD8",
                outline="",
                tags=(tag,),
            )

            wall.create_rectangle(
                x,
                y,
                x + page_w,
                y + page_h,
                fill="#FFFDFC",
                outline=accent,
                width=1,
                tags=(tag,),
            )

            wall.create_rectangle(
                x,
                y,
                x + page_w,
                y + 7 * scale,
                fill=accent,
                outline="",
                tags=(tag,),
            )

            thumb_x1 = x + 12 * scale
            thumb_y1 = y + 17 * scale
            thumb_x2 = x + page_w - 12 * scale
            thumb_y2 = y + 84 * scale

            wall.create_rectangle(
                thumb_x1,
                thumb_y1,
                thumb_x2,
                thumb_y2,
                fill=soft,
                outline=blend(accent, 0.35),
                width=1,
                tags=(tag,),
            )

            inner_w = thumb_x2 - thumb_x1
            inner_h = thumb_y2 - thumb_y1

            wall.create_rectangle(
                thumb_x1 + 7 * scale,
                thumb_y1 + 8 * scale,
                thumb_x1 + inner_w * 0.43,
                thumb_y1 + inner_h * 0.48,
                fill="#FFFFFF",
                outline=accent,
                width=1,
                tags=(tag,),
            )

            for line_index in range(4):
                yy = (
                    thumb_y1
                    + 12 * scale
                    + line_index * 8 * scale
                )
                wall.create_line(
                    thumb_x1 + inner_w * 0.52,
                    yy,
                    thumb_x2 - 7 * scale,
                    yy,
                    fill=blend(accent, 0.50),
                    width=1,
                    tags=(tag,),
                )

            wall.create_line(
                thumb_x1 + 7 * scale,
                thumb_y2 - 13 * scale,
                thumb_x2 - 7 * scale,
                thumb_y2 - 13 * scale,
                fill=blend(accent, 0.45),
                width=1,
                tags=(tag,),
            )

            title = item_title(item)

            wall.create_text(
                x + 8 * scale,
                y + 92 * scale,
                text=self._truncate(title, 18),
                fill=self.INK,
                font=(Fonts.FAMILY, max(7, int(8 * scale)), "bold"),
                anchor="nw",
                tags=(tag,),
            )

            pill_x1 = x + 8 * scale
            pill_y1 = y + 111 * scale
            pill_x2 = x + page_w - 8 * scale
            pill_y2 = y + 128 * scale

            wall.create_rectangle(
                pill_x1,
                pill_y1,
                pill_x2,
                pill_y2,
                fill=blend(status_color, 0.84),
                outline=blend(status_color, 0.35),
                width=1,
                tags=(tag,),
            )

            wall.create_text(
                (pill_x1 + pill_x2) / 2,
                (pill_y1 + pill_y2) / 2,
                text=status_text,
                fill=status_color,
                font=(Fonts.FAMILY, max(6, int(7 * scale)), "bold"),
                anchor="center",
                tags=(tag,),
            )

            if page_number is not None:
                anchor = "sw" if page_side == "left" else "se"
                number_x = (
                    x + 8 * scale
                    if page_side == "left"
                    else x + page_w - 8 * scale
                )
                wall.create_text(
                    number_x,
                    y + page_h - 5 * scale,
                    text=str(page_number),
                    fill=self.TEXT_MUTED,
                    font=(Fonts.FAMILY, max(6, int(7 * scale))),
                    anchor=anchor,
                    tags=(tag,),
                )

            if not bool(item.get("automatic_recto_verso", False)):
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

            return page_w, page_h

        def make_display_units() -> list[dict]:
            units: list[dict] = []

            if not physical_pages:
                return units

            work = list(physical_pages)

            if work and str(work[0].get("type", "")) == "couverture":
                units.append(
                    {
                        "kind": "single_cover",
                        "pages": [work.pop(0)],
                    }
                )

            back_cover = None
            if work and str(work[-1].get("type", "")) == "quatrieme":
                back_cover = work.pop()

            page_number = 1
            cursor = 0

            while cursor < len(work):
                left = work[cursor]
                right = (
                    work[cursor + 1]
                    if cursor + 1 < len(work)
                    else None
                )

                units.append(
                    {
                        "kind": "spread",
                        "pages": [left, right],
                        "left_number": page_number,
                        "right_number": (
                            page_number + 1
                            if right is not None
                            else None
                        ),
                    }
                )

                cursor += 2
                page_number += 2

            if back_cover is not None:
                units.append(
                    {
                        "kind": "single_back",
                        "pages": [back_cover],
                    }
                )

            return units

        display_units = make_display_units()

        def draw_wall(_event=None) -> None:
            width = max(1, int(wall.winfo_width()))
            viewport_h = max(1, int(wall.winfo_height()))

            if width <= 4 or viewport_h <= 4:
                return

            wall.delete("all")

            left_margin = 22
            top_margin = 78
            bottom_margin = 34

            unit_w = 246
            unit_h = 187
            gap_x = 15
            gap_y = 18

            usable_w = max(
                unit_w,
                width - left_margin * 2,
            )
            columns = max(
                1,
                int(
                    (usable_w + gap_x)
                    // (unit_w + gap_x)
                ),
            )

            rows = max(
                1,
                (len(display_units) + columns - 1)
                // columns,
            )

            content_h = max(
                viewport_h,
                top_margin
                + rows * unit_h
                + max(0, rows - 1) * gap_y
                + bottom_margin,
            )

            background = make_background(width, content_h)

            if background is not None:
                try:
                    from PIL import ImageTk

                    photo = ImageTk.PhotoImage(background)
                    wall._regulation_bg_photo = photo
                    wall.create_image(
                        0,
                        0,
                        image=photo,
                        anchor="nw",
                    )
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
                text=(
                    "Vue livre ouvert · base de la future "
                    "fenêtre Visualisation"
                ),
                fill=self.TEXT_MUTED,
                font=(Fonts.FAMILY, 8),
                anchor="nw",
            )

            if not display_units:
                wall.create_text(
                    width / 2,
                    max(130, viewport_h / 2 - 10),
                    text="Le plan du livre n'est pas encore disponible.",
                    fill=self.INK,
                    font=(Fonts.FAMILY, 12, "bold"),
                    anchor="center",
                )
                wall.create_text(
                    width / 2,
                    max(155, viewport_h / 2 + 18),
                    text=(
                        "Le Maquettage alimentera automatiquement "
                        "ce synoptique."
                    ),
                    fill=self.TEXT_MUTED,
                    font=(Fonts.FAMILY, 9),
                    anchor="center",
                )
            else:
                for index, unit in enumerate(display_units):
                    row = index // columns
                    column = index % columns

                    ux = (
                        left_margin
                        + column * (unit_w + gap_x)
                    )
                    uy = (
                        top_margin
                        + row * (unit_h + gap_y)
                    )

                    kind = unit["kind"]

                    if kind in {"single_cover", "single_back"}:
                        item = unit["pages"][0]

                        label = (
                            "COUVERTURE"
                            if kind == "single_cover"
                            else "4e DE COUVERTURE"
                        )

                        wall.create_text(
                            ux + unit_w / 2,
                            uy + 7,
                            text=label,
                            fill=self.TEXT_MUTED,
                            font=(Fonts.FAMILY, 7, "bold"),
                            anchor="n",
                        )

                        draw_page(
                            ux + (unit_w - 111) / 2,
                            uy + 24,
                            item,
                            page_side="right",
                            page_number=None,
                            scale=1.10,
                        )

                    else:
                        left_page, right_page = unit["pages"]

                        wall.create_rectangle(
                            ux + 5,
                            uy + 17,
                            ux + unit_w - 5,
                            uy + unit_h - 5,
                            fill="#FFFFFF",
                            outline=blend("#718096", 0.70),
                            width=1,
                            stipple="gray25",
                        )

                        wall.create_text(
                            ux + unit_w / 2,
                            uy + 6,
                            text="DOUBLE PAGE",
                            fill=self.TEXT_MUTED,
                            font=(Fonts.FAMILY, 7, "bold"),
                            anchor="n",
                        )

                        page_y = uy + 27
                        page_scale = 1.05
                        page_w = 101 * page_scale

                        left_x = ux + 15
                        right_x = ux + unit_w - 15 - page_w

                        draw_page(
                            left_x,
                            page_y,
                            left_page,
                            page_side="left",
                            page_number=unit["left_number"],
                            scale=page_scale,
                        )

                        if right_page is not None:
                            draw_page(
                                right_x,
                                page_y,
                                right_page,
                                page_side="right",
                                page_number=unit["right_number"],
                                scale=page_scale,
                            )
                        else:
                            wall.create_rectangle(
                                right_x,
                                page_y,
                                right_x + page_w,
                                page_y + 143 * page_scale,
                                fill="",
                                outline=blend("#AEB5BC", 0.35),
                                dash=(3, 3),
                                width=1,
                            )

                        center_x = ux + unit_w / 2
                        wall.create_line(
                            center_x,
                            page_y + 4,
                            center_x,
                            page_y + 143 * page_scale - 4,
                            fill=blend("#6B7280", 0.55),
                            width=1,
                        )

            wall.configure(
                scrollregion=(0, 0, width, content_h)
            )

        def on_mousewheel(event) -> None:
            try:
                delta = int(event.delta)
            except Exception:
                return

            if delta == 0:
                return

            wall.yview_scroll(
                -1 if delta > 0 else 1,
                "units",
            )

        wall.bind("<Configure>", draw_wall, add="+")
        wall.bind("<MouseWheel>", on_mousewheel, add="+")
        wall.after_idle(draw_wall)

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
            justify="left",
            wraplength=278,
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
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=(10, 4),
                pady=7,
            )

            ctk.CTkLabel(
                frame,
                text=value,
                font=(Fonts.FAMILY, 10, "bold"),
                text_color=color,
            ).grid(
                row=0,
                column=1,
                sticky="e",
                padx=(4, 10),
                pady=7,
            )

        metric(
            2,
            "Pages prévues",
            str(snapshot["planned_pages"]),
            self.MAQUETTAGE,
        )
        metric(
            3,
            "Pages automatiques",
            str(snapshot["automatic_pages"]),
            self.ATELIER,
        )
        metric(
            4,
            "Pages produites",
            str(snapshot["produced_pages"]),
            self.CONCEPTION,
        )
        metric(
            5,
            "Pages validées",
            str(snapshot["validated_pages"]),
            self.VERIFICATION,
        )

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

        work_pages = max(
            0,
            snapshot["planned_pages"] - snapshot["automatic_pages"]
        )
        remaining_to_produce = max(
            0,
            work_pages - snapshot["produced_pages"]
        )

        alerts: list[tuple[str, str]] = []

        if not snapshot["items"]:
            alerts.append(
                (
                    "Plan du livre",
                    "Le Maquettage doit encore définir la structure.",
                )
            )
        elif remaining_to_produce:
            alerts.append(
                (
                    "Production",
                    f"{remaining_to_produce} page(s) restent à produire.",
                )
            )

        if (
            snapshot["produced_pages"] > snapshot["validated_pages"]
            and snapshot["produced_pages"] > 0
        ):
            alerts.append(
                (
                    "Validation",
                    (
                        f"{snapshot['produced_pages'] - snapshot['validated_pages']} "
                        "page(s) produite(s) non validée(s)."
                    ),
                )
            )

        if not alerts:
            alerts.append(
                (
                    "Aucune alerte",
                    "Le projet ne demande pas d'intervention immédiate.",
                )
            )

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
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=9,
                pady=(6, 0),
            )

            ctk.CTkLabel(
                alert,
                text=text,
                font=(Fonts.FAMILY, 8),
                text_color=self.TEXT_MUTED,
                anchor="w",
                justify="left",
                wraplength=260,
            ).grid(
                row=1,
                column=0,
                sticky="ew",
                padx=9,
                pady=(1, 7),
            )

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
"""


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
        if (
            lines[index].startswith("    def ")
            or lines[index].startswith("    @")
        ):
            end = index
            break

    return "".join(lines[start:end])


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER_NEW in original:
        print("CENTRE_VISUALISATION_DOUBLE_PAGE_V2_DEJA_APPLIQUE")
        return

    if MARKER_REQUIRED not in original:
        fail("Centre de régulation V1 non détecté")

    old_method = get_method(
        original,
        "_create_main_workspace",
    )

    candidate = original.replace(
        old_method,
        NEW_METHOD.rstrip() + "\n\n",
        1,
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
        / f"document_view_avant_double_page_v2_{stamp}.py"
    )
    temp = TARGET.with_suffix(".double_page_v2.tmp")

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

    print("CENTRE_VISUALISATION_DOUBLE_PAGE_V2_OK")
    print("Couverture seule, doubles pages, quatrième seule.")
    print("Vignettes légèrement agrandies.")
    print("Statut Maquettage séparé du type de page.")
    print("Défilement vertical activé pour les livres longs.")
    print("Le ruban permanent reste inchangé.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
