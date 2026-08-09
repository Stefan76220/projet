from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"

MARKER = "TRANSFERT_VISIBLE_HEADER_ATELIER_V2"
REQUIRED = "TRANSFERT_DIRECT_EDITEUR_ATELIER_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    if REQUIRED not in source:
        fail("le premier correctif Transférer n'est pas détecté")

    # Retire le groupe hors-écran du grand ruban.
    old_group = (
        "        # TRANSFERT_DIRECT_EDITEUR_ATELIER_V1\n"
        "        _, conception = group(\"Conception\", 108, coral, coral_soft)\n"
        "        icon_button(\n"
        "            conception,\n"
        "            \"⇢\",\n"
        "            \"Transférer\",\n"
        "            self._transfer_current_to_conception,\n"
        "            width=84,\n"
        "            state=(\n"
        "                \"normal\"\n"
        "                if self._on_transfer_to_conception is not None\n"
        "                else \"disabled\"\n"
        "            ),\n"
        "            accent=coral,\n"
        "            soft=coral_soft,\n"
        "        )\n"
        "\n"
    )
    if old_group not in source:
        fail("ancien bloc Conception hors écran introuvable")

    source = source.replace(old_group, "", 1)

    # Surcharge seulement l'en-tête Atelier :
    # elle conserve l'en-tête existant puis insère Transférer avant
    # les commandes de droite.
    anchor = "    def _create_alignment_toolbar(self, parent) -> None:\n"

    header_method = (
        "    def _create_header(self, parent) -> None:\n"
        "        # TRANSFERT_VISIBLE_HEADER_ATELIER_V2\n"
        "        super()._create_header(parent)\n"
        "\n"
        "        children = parent.winfo_children()\n"
        "        if not children:\n"
        "            return\n"
        "\n"
        "        header = children[-1]\n"
        "\n"
        "        # Décale les commandes existantes de droite d'une colonne.\n"
        "        for widget in header.grid_slaves():\n"
        "            info = widget.grid_info()\n"
        "            try:\n"
        "                column = int(info.get(\"column\", 0))\n"
        "            except (TypeError, ValueError):\n"
        "                continue\n"
        "            if column >= 3:\n"
        "                widget.grid_configure(column=column + 1)\n"
        "\n"
        "        transfer_button = ctk.CTkButton(\n"
        "            header,\n"
        "            text=\"⇢  Transférer\",\n"
        "            width=108,\n"
        "            height=30,\n"
        "            corner_radius=8,\n"
        "            fg_color=\"#F2DDD6\",\n"
        "            hover_color=\"#EBC9BF\",\n"
        "            text_color=\"#B65F4B\",\n"
        "            border_width=1,\n"
        "            border_color=\"#DF806B\",\n"
        "            font=(Fonts.FAMILY, 11, \"bold\"),\n"
        "            command=self._transfer_current_to_conception,\n"
        "            state=(\n"
        "                \"normal\"\n"
        "                if self._on_transfer_to_conception is not None\n"
        "                else \"disabled\"\n"
        "            ),\n"
        "        )\n"
        "        transfer_button.grid(\n"
        "            row=0,\n"
        "            column=3,\n"
        "            padx=(0, 8),\n"
        "            pady=9,\n"
        "            sticky=\"e\",\n"
        "        )\n"
        "        transfer_button.bind(\n"
        "            \"<Enter>\",\n"
        "            lambda _event: self._show_editor_tool_name(\n"
        "                \"Transférer ce gabarit vers Conception\"\n"
        "            ),\n"
        "            add=\"+\",\n"
        "        )\n"
        "        transfer_button.bind(\n"
        "            \"<Leave>\",\n"
        "            self._restore_editor_tool_status,\n"
        "            add=\"+\",\n"
        "        )\n"
        "\n"
    )

    if anchor not in source:
        fail("méthode du ruban Atelier introuvable")

    source = source.replace(anchor, header_method + anchor, 1)

    return source


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
        print("TRANSFERT_VISIBLE_HEADER_ATELIER_V2_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"model_workshop_view_avant_transfert_visible_{stamp}.py"
    )
    temp = TARGET.with_suffix(".transfert_visible.tmp")

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

    print("TRANSFERT_VISIBLE_HEADER_ATELIER_V2_OK")
    print("Transférer est maintenant placé dans la barre supérieure.")
    print("L'ancien bloc hors écran a été supprimé.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
