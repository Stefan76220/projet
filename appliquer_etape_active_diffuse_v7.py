from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"
MARKER = "ETAPE_ACTIVE_DIFFUSE_V7"

OLD = '        def draw_item(\n            *,\n            cx: float,\n            icon_kind: str,\n            label: str,\n            color: str,\n            command=None,\n            active: bool = False,\n            enabled: bool = True,\n            width: float = 86,\n        ) -> None:\n            item_color = color if (enabled or active) else self.TEXT_LIGHT\n\n            draw_icon(\n                icon_kind,\n                cx,\n                45,\n                item_color,\n            )\n\n            canvas.create_text(\n                cx,\n                69,\n                text=label,\n                fill=self.INK if active else item_color,\n                font=(\n                    Fonts.FAMILY,\n                    9,\n                    "bold" if active else "normal",\n                ),\n                anchor="center",\n            )\n\n            if active:\n                canvas.create_line(\n                    cx - 16, 82,\n                    cx + 16, 82,\n                    fill=item_color,\n                    width=2,\n                )\n            else:\n                canvas.create_oval(\n                    cx - 1.5, 81,\n                    cx + 1.5, 84,\n                    fill=item_color,\n                    outline="",\n                )\n\n            add_click_region(\n                cx - width / 2,\n                cx + width / 2,\n                command,\n                enabled,\n            )\n'
NEW = '        def draw_item(\n            *,\n            cx: float,\n            icon_kind: str,\n            label: str,\n            color: str,\n            command=None,\n            active: bool = False,\n            enabled: bool = True,\n            width: float = 86,\n        ) -> None:\n            # ETAPE_ACTIVE_DIFFUSE_V7\n            # L\'étape courante est un repère, pas un bouton :\n            # elle est plus claire, non cliquable et reçoit un halo\n            # tramé qui laisse réellement voir le décor principal.\n            if active:\n                rgb = hex_to_rgb(color)\n                active_rgb = tuple(\n                    int(round(channel + (255 - channel) * 0.30))\n                    for channel in rgb\n                )\n                item_color = "#{:02X}{:02X}{:02X}".format(*active_rgb)\n\n                halo_rgb = tuple(\n                    int(round(channel + (255 - channel) * 0.72))\n                    for channel in rgb\n                )\n                halo_color = "#{:02X}{:02X}{:02X}".format(*halo_rgb)\n\n                canvas.create_oval(\n                    cx - width * 0.43,\n                    24,\n                    cx + width * 0.43,\n                    86,\n                    fill=halo_color,\n                    outline="",\n                    stipple="gray25",\n                )\n            else:\n                item_color = color if enabled else self.TEXT_LIGHT\n\n            draw_icon(\n                icon_kind,\n                cx,\n                45,\n                item_color,\n            )\n\n            canvas.create_text(\n                cx,\n                69,\n                text=label,\n                fill=item_color,\n                font=(\n                    Fonts.FAMILY,\n                    9,\n                    "bold" if active else "normal",\n                ),\n                anchor="center",\n            )\n\n            if active:\n                canvas.create_line(\n                    cx - 16, 82,\n                    cx + 16, 82,\n                    fill=item_color,\n                    width=2,\n                )\n            else:\n                canvas.create_oval(\n                    cx - 1.5, 81,\n                    cx + 1.5, 84,\n                    fill=item_color,\n                    outline="",\n                )\n\n            # Une étape active n\'est jamais cliquable, même si une\n            # commande lui était attribuée par erreur plus tard.\n            add_click_region(\n                cx - width / 2,\n                cx + width / 2,\n                None if active else command,\n                enabled and not active,\n            )\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("ETAPE_ACTIVE_DIFFUSE_DEJA_APPLIQUEE")
        return

    if OLD not in original:
        fail(
            "le bloc draw_item attendu n'a pas été trouvé. "
            "Le fichier a probablement changé depuis la V6."
        )

    candidate = original.replace(OLD, NEW, 1)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_etape_active_diffuse_{stamp}.py"
    temp = TARGET.with_suffix(".active_diffuse.tmp")

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

    print("ETAPE_ACTIVE_DIFFUSE_V7_OK")
    print("Centre est maintenant plus clair et explicitement non cliquable.")
    print("Un halo tramé très léger laisse passer le décor principal.")
    print("La position et les fonctions des autres accès sont inchangées.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
