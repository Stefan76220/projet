from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

MARKER = "REGULATION_ECRAN_CONTROLE_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    start_anchor = (
        "        side = ctk.CTkFrame(\n"
        "            workspace,\n"
        "            width=314,\n"
    )
    end_anchor = (
        "        return workspace\n"
        "\n"
        "    def _create_side_navigation"
    )

    start = source.find(start_anchor)
    if start < 0:
        fail("début du panneau Régulation introuvable")

    end = source.find(end_anchor, start)
    if end < 0:
        fail("fin du panneau Régulation introuvable")

    new_panel = '''        # REGULATION_ECRAN_CONTROLE_V1
        side = ctk.CTkFrame(
            workspace,
            width=314,
            fg_color="#FAFBF9",
            corner_radius=9,
            border_width=1,
            border_color=self.BORDER,
        )
        side.grid(row=0, column=1, sticky="nsew")
        side.grid_propagate(False)
        side.grid_columnconfigure((0, 1), weight=1, uniform="regulation_cols")

        ctk.CTkLabel(
            side,
            text="Régulation",
            font=(Fonts.FAMILY, 13, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=14,
            pady=(13, 1),
        )

        ctk.CTkLabel(
            side,
            text="État chiffré, progression et alertes du projet.",
            font=(Fonts.FAMILY, 8),
            text_color=self.TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=280,
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=14,
            pady=(0, 9),
        )

        status_counts = {
            "MAQUETTAGE": 0,
            "GABARIT": 0,
            "À PRODUIRE": 0,
            "PRODUITE": 0,
            "AUTO": 0,
        }

        for regulation_item in physical_pages:
            status_label = page_status(regulation_item)[0]
            if status_label.startswith("AUTO"):
                status_counts["AUTO"] += 1
            elif status_label in status_counts:
                status_counts[status_label] += 1

        planned_count = len(physical_pages)
        automatic_count = status_counts["AUTO"]
        work_count = max(0, planned_count - automatic_count)
        mockup_count = status_counts["MAQUETTAGE"]
        gabarit_count = status_counts["GABARIT"]
        ready_count = status_counts["À PRODUIRE"]
        produced_count = status_counts["PRODUITE"]
        validated_count = min(
            work_count,
            max(0, int(snapshot.get("validated_pages", 0) or 0)),
        )

        prepared_count = min(
            work_count,
            gabarit_count + ready_count + produced_count,
        )
        transferred_count = min(
            work_count,
            ready_count + produced_count,
        )

        ctk.CTkLabel(
            side,
            text="État du livre",
            font=(Fonts.FAMILY, 9, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=14,
            pady=(1, 5),
        )

        def control_metric(
            row: int,
            column: int,
            label: str,
            value: int,
            color: str,
        ) -> None:
            card = ctk.CTkFrame(
                side,
                height=43,
                fg_color=blend(color, 0.90),
                corner_radius=7,
                border_width=1,
                border_color=blend(color, 0.58),
            )
            card.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(12 if column == 0 else 3, 3 if column == 0 else 12),
                pady=(0, 5),
            )
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card,
                text=label,
                font=(Fonts.FAMILY, 7),
                text_color=self.TEXT_MUTED,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=(8, 3),
                pady=(7, 0),
            )

            ctk.CTkLabel(
                card,
                text=str(value),
                font=(Fonts.FAMILY, 13, "bold"),
                text_color=color,
                anchor="e",
            ).grid(
                row=0,
                column=1,
                rowspan=2,
                sticky="e",
                padx=(3, 8),
                pady=5,
            )

        control_metric(3, 0, "Pages prévues", planned_count, self.MAQUETTAGE)
        control_metric(3, 1, "Automatiques", automatic_count, self.ATELIER)
        control_metric(4, 0, "Sans gabarit", mockup_count, self.MAQUETTAGE)
        control_metric(4, 1, "Gabarits", gabarit_count, self.ATELIER)
        control_metric(5, 0, "À produire", ready_count, self.CONCEPTION)
        control_metric(5, 1, "Produites", produced_count, self.CONCEPTION)
        control_metric(6, 0, "Validées", validated_count, self.VERIFICATION)

        watch_card = ctk.CTkFrame(
            side,
            height=43,
            fg_color="#F4F6F4",
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
        )
        watch_card.grid(
            row=6,
            column=1,
            sticky="ew",
            padx=(3, 12),
            pady=(0, 5),
        )
        watch_card.grid_propagate(False)
        watch_card.grid_columnconfigure(0, weight=1)

        alert_page_count = (
            mockup_count
            + ready_count
            + max(0, produced_count - validated_count)
        )
        ctk.CTkLabel(
            watch_card,
            text="À surveiller",
            font=(Fonts.FAMILY, 7),
            text_color=self.TEXT_MUTED,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(8, 3),
            pady=(7, 0),
        )
        ctk.CTkLabel(
            watch_card,
            text=str(alert_page_count),
            font=(Fonts.FAMILY, 13, "bold"),
            text_color="#C27B4A" if alert_page_count else "#5F8A6A",
            anchor="e",
        ).grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="e",
            padx=(3, 8),
            pady=5,
        )

        ctk.CTkLabel(
            side,
            text="Progression",
            font=(Fonts.FAMILY, 9, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=14,
            pady=(8, 5),
        )

        progress_frame = ctk.CTkFrame(
            side,
            fg_color="transparent",
            corner_radius=0,
        )
        progress_frame.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
        )
        progress_frame.grid_columnconfigure(0, weight=1)

        def progress_line(
            row: int,
            label: str,
            value: int,
            total: int,
            color: str,
        ) -> None:
            total = max(0, int(total))
            value = max(0, min(int(value), total)) if total else 0
            ratio = (value / total) if total else 0.0

            label_row = ctk.CTkFrame(
                progress_frame,
                fg_color="transparent",
                corner_radius=0,
            )
            label_row.grid(row=row * 2, column=0, sticky="ew")
            label_row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                label_row,
                text=label,
                font=(Fonts.FAMILY, 7),
                text_color=self.TEXT_MUTED,
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                label_row,
                text=f"{value} / {total}",
                font=(Fonts.FAMILY, 7, "bold"),
                text_color=color,
                anchor="e",
            ).grid(row=0, column=1, sticky="e")

            bar = ctk.CTkProgressBar(
                progress_frame,
                height=7,
                corner_radius=4,
                fg_color="#E7EAE6",
                progress_color=color,
            )
            bar.grid(
                row=row * 2 + 1,
                column=0,
                sticky="ew",
                pady=(1, 5),
            )
            bar.set(ratio)

        progress_line(
            0,
            "Gabarits préparés",
            prepared_count,
            work_count,
            self.ATELIER,
        )
        progress_line(
            1,
            "Transférés vers Conception",
            transferred_count,
            work_count,
            self.CONCEPTION,
        )
        progress_line(
            2,
            "Pages produites",
            produced_count,
            work_count,
            self.CONCEPTION,
        )
        progress_line(
            3,
            "Pages validées",
            validated_count,
            work_count,
            self.VERIFICATION,
        )

        ctk.CTkLabel(
            side,
            text="Alertes / À surveiller",
            font=(Fonts.FAMILY, 9, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=9,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=14,
            pady=(8, 5),
        )

        alerts: list[tuple[str, str, str]] = []

        if not physical_pages:
            alerts.append(
                (
                    "attention",
                    "Plan du livre",
                    "Le Maquettage doit encore définir la structure du livre.",
                )
            )
        else:
            if mockup_count:
                alerts.append(
                    (
                        "attention",
                        "Gabarits",
                        f"{mockup_count} page(s) n'ont pas encore de gabarit.",
                    )
                )

            if ready_count:
                alerts.append(
                    (
                        "information",
                        "Conception",
                        f"{ready_count} page(s) sont prêtes à produire.",
                    )
                )

            waiting_validation = max(0, produced_count - validated_count)
            if waiting_validation:
                alerts.append(
                    (
                        "attention",
                        "Validation",
                        f"{waiting_validation} page(s) produite(s) restent à valider.",
                    )
                )

        if not alerts:
            alerts.append(
                (
                    "ok",
                    "Projet cohérent",
                    "Aucun point ne demande d'attention immédiate.",
                )
            )

        alert_colors = {
            "information": ("#EAF3F7", "#6B9DB5"),
            "attention": ("#FBF2E7", "#C27B4A"),
            "erreur": ("#F9E9E7", "#BE5B52"),
            "ok": ("#EAF3EC", "#5F8A6A"),
        }

        alerts_frame = ctk.CTkFrame(
            side,
            fg_color="transparent",
            corner_radius=0,
        )
        alerts_frame.grid(
            row=10,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
            pady=(0, 9),
        )
        alerts_frame.grid_columnconfigure(0, weight=1)

        for alert_row, (severity, title, text) in enumerate(alerts[:4]):
            soft_color, accent_color = alert_colors[severity]
            alert = ctk.CTkFrame(
                alerts_frame,
                fg_color=soft_color,
                corner_radius=7,
                border_width=1,
                border_color=blend(accent_color, 0.48),
            )
            alert.grid(
                row=alert_row,
                column=0,
                sticky="ew",
                pady=(0, 4),
            )
            alert.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                alert,
                text="●",
                font=(Fonts.FAMILY, 8, "bold"),
                text_color=accent_color,
            ).grid(
                row=0,
                column=0,
                rowspan=2,
                sticky="n",
                padx=(8, 5),
                pady=(7, 0),
            )

            ctk.CTkLabel(
                alert,
                text=title,
                font=(Fonts.FAMILY, 8, "bold"),
                text_color=self.INK,
                anchor="w",
            ).grid(
                row=0,
                column=1,
                sticky="ew",
                padx=(0, 8),
                pady=(5, 0),
            )

            ctk.CTkLabel(
                alert,
                text=text,
                font=(Fonts.FAMILY, 7),
                text_color=self.TEXT_MUTED,
                anchor="w",
                justify="left",
                wraplength=238,
            ).grid(
                row=1,
                column=1,
                sticky="ew",
                padx=(0, 8),
                pady=(0, 6),
            )

'''

    return source[:start] + new_panel + source[end:]


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    source = TARGET.read_text(encoding="utf-8")
    candidate = patch(source)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    if candidate == source:
        print("REGULATION_ECRAN_CONTROLE_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_regulation_controle_{stamp}.py"
    )
    temp = TARGET.with_suffix(".regulation_controle.tmp")

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

    print("REGULATION_ECRAN_CONTROLE_V1_OK")
    print("Régulation affiche maintenant état, progression et alertes.")
    print("Le synoptique n'est pas modifié.")
    print("Nettoyage n'est plus affiché dans Régulation.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
