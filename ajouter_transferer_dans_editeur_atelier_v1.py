from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"

MARKER = "TRANSFERT_DIRECT_EDITEUR_ATELIER_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    init_old = (
        "        on_back=None,\n"
        "        on_new=None,\n"
        "        on_ready: Callable[[], None] | None = None,\n"
        "    ) -> None:\n"
        "        super().__init__(parent, page, on_back=on_back)\n"
        "        self._on_new_creation = on_new\n"
        "        self._on_ready = on_ready\n"
    )
    init_new = (
        "        on_back=None,\n"
        "        on_new=None,\n"
        "        on_transfer=None,\n"
        "        on_ready: Callable[[], None] | None = None,\n"
        "    ) -> None:\n"
        "        super().__init__(parent, page, on_back=on_back)\n"
        "        self._on_new_creation = on_new\n"
        "        self._on_transfer_to_conception = on_transfer\n"
        "        self._on_ready = on_ready\n"
    )
    if init_old not in source:
        fail("constructeur de AtelierPageEditorView introuvable")
    source = source.replace(init_old, init_new, 1)

    toolbar_old = (
        "        self._toggle_panel_button = icon_button(\n"
        "            panel,\n"
        '            "▤",\n'
        '            "Panneau",\n'
        "            self._toggle_properties_panel,\n"
        "            width=84,\n"
        "            accent=lilac,\n"
        "            soft=lilac_soft,\n"
        "        )\n"
        "\n"
        "        self._refresh_group_controls()\n"
    )
    toolbar_new = (
        "        self._toggle_panel_button = icon_button(\n"
        "            panel,\n"
        '            "▤",\n'
        '            "Panneau",\n'
        "            self._toggle_properties_panel,\n"
        "            width=84,\n"
        "            accent=lilac,\n"
        "            soft=lilac_soft,\n"
        "        )\n"
        "\n"
        "        # TRANSFERT_DIRECT_EDITEUR_ATELIER_V1\n"
        '        _, conception = group("Conception", 108, coral, coral_soft)\n'
        "        icon_button(\n"
        "            conception,\n"
        '            "⇢",\n'
        '            "Transférer",\n'
        "            self._transfer_current_to_conception,\n"
        "            width=84,\n"
        "            state=(\n"
        '                "normal"\n'
        "                if self._on_transfer_to_conception is not None\n"
        '                else "disabled"\n'
        "            ),\n"
        "            accent=coral,\n"
        "            soft=coral_soft,\n"
        "        )\n"
        "\n"
        "        self._refresh_group_controls()\n"
    )
    if toolbar_old not in source:
        fail("bloc Affichage du ruban Atelier introuvable")
    source = source.replace(toolbar_old, toolbar_new, 1)

    method_anchor = (
        "    def _set_active_editor_tool(self, tool_key: str) -> None:\n"
    )
    method = (
        "    def _transfer_current_to_conception(self) -> None:\n"
        "        callback = self._on_transfer_to_conception\n"
        "        if callback is not None:\n"
        "            callback()\n"
        "\n"
    )
    if method_anchor not in source:
        fail("point d'insertion de l'action Transférer introuvable")
    source = source.replace(method_anchor, method + method_anchor, 1)

    initial_old = (
        "            on_back=self._back,\n"
        "            on_new=self._new_creation,\n"
        "            on_ready=lambda: self._reveal_initial_editor(\n"
    )
    initial_new = (
        "            on_back=self._back,\n"
        "            on_new=self._new_creation,\n"
        "            on_transfer=self._transfer_current_model_from_editor,\n"
        "            on_ready=lambda: self._reveal_initial_editor(\n"
    )
    if initial_old not in source:
        fail("création initiale de l'éditeur Atelier introuvable")
    source = source.replace(initial_old, initial_new, 1)

    staged_old = (
        "            on_back=self._back,\n"
        "            on_new=self._new_creation,\n"
        "            on_ready=lambda: self._stage_ready(\n"
    )
    staged_new = (
        "            on_back=self._back,\n"
        "            on_new=self._new_creation,\n"
        "            on_transfer=self._transfer_current_model_from_editor,\n"
        "            on_ready=lambda: self._stage_ready(\n"
    )
    if staged_old not in source:
        fail("création différée de l'éditeur Atelier introuvable")
    source = source.replace(staged_old, staged_new, 1)

    transfer_anchor = "    def _open_transfer(self) -> None:\n"
    transfer_method = (
        "    def _transfer_current_model_from_editor(self) -> None:\n"
        "        identifier = str(self._working_model_id or \"\").strip()\n"
        "        if not identifier:\n"
        "            messagebox.showinfo(\n"
        '                "Gabarit non enregistré",\n'
        "                (\n"
        '                    "Enregistre d’abord cette création comme gabarit du projet, "\n'
        '                    "puis transfère-la vers Conception."\n'
        "                ),\n"
        "                parent=self.parent.winfo_toplevel(),\n"
        "            )\n"
        "            return\n"
        "\n"
        "        model = next(\n"
        "            (\n"
        "                candidate\n"
        "                for candidate in self._load_project_models()\n"
        "                if str(candidate.identifier) == identifier\n"
        "            ),\n"
        "            None,\n"
        "        )\n"
        "        if model is None:\n"
        "            messagebox.showinfo(\n"
        '                "Gabarit introuvable",\n'
        '                "Le gabarit actuellement ouvert n’existe plus dans le projet.",\n'
        "                parent=self.parent.winfo_toplevel(),\n"
        "            )\n"
        "            return\n"
        "\n"
        "        self._transfer_models([model])\n"
        "\n"
    )
    if transfer_anchor not in source:
        fail("méthode _open_transfer introuvable")
    source = source.replace(
        transfer_anchor,
        transfer_method + transfer_anchor,
        1,
    )

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
        print("TRANSFERT_DIRECT_EDITEUR_ATELIER_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"model_workshop_view_avant_transfert_direct_{stamp}.py"
    )
    temp = TARGET.with_suffix(".transfert_direct.tmp")

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

    print("TRANSFERT_DIRECT_EDITEUR_ATELIER_V1_OK")
    print("Le ruban de l'éditeur Atelier possède maintenant Transférer.")
    print("Le bouton transfère uniquement le gabarit actuellement ouvert.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
