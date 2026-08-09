from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

MARKER = "REGULATION_ETAT_COMPACT_V1"
REQUIRED = "REGULATION_ECRAN_CONTROLE_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    if REQUIRED not in source:
        fail("l'écran de contrôle Régulation n'est pas détecté")

    state_start = (
        '        ctk.CTkLabel(\n'
        '            side,\n'
        '            text="État du livre",\n'
    )
    progress_start = (
        '        ctk.CTkLabel(\n'
        '            side,\n'
        '            text="Progression",\n'
    )

    start = source.find(state_start)
    if start < 0:
        fail("zone État du livre introuvable")

    end = source.find(progress_start, start)
    if end < 0:
        fail("zone Progression introuvable")

    compact = (
        '        # REGULATION_ETAT_COMPACT_V1\n'
        '        ctk.CTkLabel(\n'
        '            side,\n'
        '            text="État du livre",\n'
        '            font=(Fonts.FAMILY, 9, "bold"),\n'
        '            text_color=self.INK,\n'
        '            anchor="w",\n'
        '        ).grid(\n'
        '            row=2,\n'
        '            column=0,\n'
        '            columnspan=2,\n'
        '            sticky="ew",\n'
        '            padx=14,\n'
        '            pady=(1, 5),\n'
        '        )\n'
        '\n'
        '        alert_page_count = (\n'
        '            mockup_count\n'
        '            + ready_count\n'
        '            + max(0, produced_count - validated_count)\n'
        '        )\n'
        '\n'
        '        metrics_strip = ctk.CTkFrame(\n'
        '            side,\n'
        '            height=58,\n'
        '            fg_color="#F5F7F5",\n'
        '            corner_radius=8,\n'
        '            border_width=1,\n'
        '            border_color=self.BORDER,\n'
        '        )\n'
        '        metrics_strip.grid(\n'
        '            row=3,\n'
        '            column=0,\n'
        '            columnspan=2,\n'
        '            sticky="ew",\n'
        '            padx=12,\n'
        '            pady=(0, 3),\n'
        '        )\n'
        '        metrics_strip.grid_propagate(False)\n'
        '\n'
        '        for metric_column in range(4):\n'
        '            metrics_strip.grid_columnconfigure(\n'
        '                metric_column,\n'
        '                weight=1,\n'
        '                uniform="regulation_metrics",\n'
        '            )\n'
        '\n'
        '        def compact_metric(\n'
        '            column: int,\n'
        '            label: str,\n'
        '            value: int,\n'
        '            color: str,\n'
        '        ) -> None:\n'
        '            cell = ctk.CTkFrame(\n'
        '                metrics_strip,\n'
        '                fg_color="transparent",\n'
        '                corner_radius=0,\n'
        '            )\n'
        '            cell.grid(\n'
        '                row=0,\n'
        '                column=column,\n'
        '                sticky="nsew",\n'
        '                padx=2,\n'
        '                pady=4,\n'
        '            )\n'
        '            cell.grid_columnconfigure(0, weight=1)\n'
        '\n'
        '            ctk.CTkLabel(\n'
        '                cell,\n'
        '                text=str(value),\n'
        '                font=(Fonts.FAMILY, 14, "bold"),\n'
        '                text_color=color,\n'
        '            ).grid(\n'
        '                row=0,\n'
        '                column=0,\n'
        '                sticky="s",\n'
        '                pady=(1, 0),\n'
        '            )\n'
        '\n'
        '            ctk.CTkLabel(\n'
        '                cell,\n'
        '                text=label,\n'
        '                font=(Fonts.FAMILY, 6),\n'
        '                text_color=self.TEXT_MUTED,\n'
        '            ).grid(\n'
        '                row=1,\n'
        '                column=0,\n'
        '                sticky="n",\n'
        '                pady=(0, 1),\n'
        '            )\n'
        '\n'
        '        compact_metric(0, "Pages", planned_count, self.MAQUETTAGE)\n'
        '        compact_metric(1, "Gabarits", gabarit_count, self.ATELIER)\n'
        '        compact_metric(2, "À produire", ready_count, self.CONCEPTION)\n'
        '        compact_metric(3, "Validées", validated_count, self.VERIFICATION)\n'
        '\n'
        '        ctk.CTkLabel(\n'
        '            side,\n'
        '            text=(\n'
        '                f"Auto {automatic_count}"\n'
        '                f"   ·   Sans gabarit {mockup_count}"\n'
        '                f"   ·   Produites {produced_count}"\n'
        '                f"   ·   À surveiller {alert_page_count}"\n'
        '            ),\n'
        '            font=(Fonts.FAMILY, 6),\n'
        '            text_color=self.TEXT_MUTED,\n'
        '            anchor="center",\n'
        '            justify="center",\n'
        '        ).grid(\n'
        '            row=4,\n'
        '            column=0,\n'
        '            columnspan=2,\n'
        '            sticky="ew",\n'
        '            padx=12,\n'
        '            pady=(0, 5),\n'
        '        )\n'
        '\n'
    )

    candidate = source[:start] + compact + source[end:]

    replacements = [
        (
            '            row=7,\n'
            '            column=0,\n'
            '            columnspan=2,\n'
            '            sticky="ew",\n'
            '            padx=14,\n'
            '            pady=(8, 5),\n',
            '            row=5,\n'
            '            column=0,\n'
            '            columnspan=2,\n'
            '            sticky="ew",\n'
            '            padx=14,\n'
            '            pady=(6, 5),\n',
        ),
        (
            '            row=8,\n'
            '            column=0,\n'
            '            columnspan=2,\n'
            '            sticky="ew",\n'
            '            padx=12,\n',
            '            row=6,\n'
            '            column=0,\n'
            '            columnspan=2,\n'
            '            sticky="ew",\n'
            '            padx=12,\n',
        ),
        (
            '            row=9,\n'
            '            column=0,\n'
            '            columnspan=2,\n'
            '            sticky="ew",\n'
            '            padx=14,\n'
            '            pady=(8, 5),\n',
            '            row=7,\n'
            '            column=0,\n'
            '            columnspan=2,\n'
            '            sticky="ew",\n'
            '            padx=14,\n'
            '            pady=(6, 5),\n',
        ),
        (
            '            row=10,\n'
            '            column=0,\n'
            '            columnspan=2,\n'
            '            sticky="ew",\n'
            '            padx=12,\n'
            '            pady=(0, 9),\n',
            '            row=8,\n'
            '            column=0,\n'
            '            columnspan=2,\n'
            '            sticky="ew",\n'
            '            padx=12,\n'
            '            pady=(0, 9),\n',
        ),
    ]

    for old, new in replacements:
        if old not in candidate:
            fail("un repère de mise en page de Régulation a changé")
        candidate = candidate.replace(old, new, 1)

    return candidate


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
        print("REGULATION_ETAT_COMPACT_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_etat_compact_{stamp}.py"
    )
    temp = TARGET.with_suffix(".etat_compact.tmp")

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

    print("REGULATION_ETAT_COMPACT_V1_OK")
    print("État du livre tient maintenant dans une bande compacte.")
    print("Progression et Alertes ont été remontées.")
    print("Les calculs et le synoptique ne sont pas modifiés.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
