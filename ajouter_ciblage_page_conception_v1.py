from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_editor_view.py"

MARKER = "CIBLAGE_PAGE_CONCEPTION_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    init_anchor = (
        "        self.change_type_dialog: ChangePageTypeDialog | None = None\n"
        "\n"
        "        self.page_type_library = PageTypeLibrary()\n"
    )
    init_new = (
        "        self.change_type_dialog: ChangePageTypeDialog | None = None\n"
        "\n"
        "        # CIBLAGE_PAGE_CONCEPTION_V1\n"
        "        self._active_page_number: int | None = None\n"
        "\n"
        "        self.page_type_library = PageTypeLibrary()\n"
    )
    if init_anchor not in source:
        fail("point d'initialisation de DocumentEditorView introuvable")
    source = source.replace(init_anchor, init_new, 1)

    show_anchor = (
        "    def show(self) -> None:\n"
        "        self.document = (\n"
        "            self.application.document_manager.get_document()\n"
        "        )\n"
        "\n"
        "        self._clear_parent()\n"
    )
    show_new = (
        "    def show(self) -> None:\n"
        "        self.document = (\n"
        "            self.application.document_manager.get_document()\n"
        "        )\n"
        "        self._active_page_number = None\n"
        "\n"
        "        self._clear_parent()\n"
    )
    if show_anchor not in source:
        fail("méthode show de DocumentEditorView introuvable")
    source = source.replace(show_anchor, show_new, 1)

    open_old = (
        "    def open_page(self, page_info) -> None:\n"
        "        if self.document is None:\n"
        "            return\n"
        "\n"
        "        try:\n"
        "            page = self.document.get_page(\n"
        "                page_info[\"numero\"],\n"
        "            )\n"
        "\n"
        "            if page is None:\n"
        "                return\n"
        "\n"
        "            PageEditorView(\n"
        "                self.parent,\n"
        "                page,\n"
        "                on_back=self.show,\n"
        "            ).show()\n"
        "\n"
        "        except Exception:\n"
        "            traceback.print_exc()\n"
    )

    open_new = (
        "    @property\n"
        "    def active_page_number(self) -> int | None:\n"
        "        \"\"\"Numéro de la page actuellement ouverte dans Conception.\"\"\"\n"
        "        return self._active_page_number\n"
        "\n"
        "    def focus_page(self, page_number: int) -> bool:\n"
        "        \"\"\"Ouvre directement une page précise dans le Bureau Conception.\"\"\"\n"
        "        self.document = (\n"
        "            self.application.document_manager.get_document()\n"
        "        )\n"
        "        if self.document is None:\n"
        "            return False\n"
        "\n"
        "        try:\n"
        "            number = int(page_number)\n"
        "        except (TypeError, ValueError):\n"
        "            return False\n"
        "\n"
        "        try:\n"
        "            page = self.document.get_page(number)\n"
        "        except Exception:\n"
        "            traceback.print_exc()\n"
        "            return False\n"
        "\n"
        "        if page is None:\n"
        "            return False\n"
        "\n"
        "        self._active_page_number = number\n"
        "\n"
        "        try:\n"
        "            PageEditorView(\n"
        "                self.parent,\n"
        "                page,\n"
        "                on_back=self.show,\n"
        "            ).show()\n"
        "        except Exception:\n"
        "            self._active_page_number = None\n"
        "            traceback.print_exc()\n"
        "            return False\n"
        "\n"
        "        return True\n"
        "\n"
        "    def open_page(self, page_info) -> None:\n"
        "        try:\n"
        "            self.focus_page(page_info[\"numero\"])\n"
        "        except (KeyError, TypeError):\n"
        "            return\n"
    )

    if open_old not in source:
        fail("méthode open_page attendue introuvable")
    source = source.replace(open_old, open_new, 1)

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
        print("CIBLAGE_PAGE_CONCEPTION_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_editor_view_avant_ciblage_conception_{stamp}.py"
    )
    temp = TARGET.with_suffix(".ciblage_conception.tmp")

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

    print("CIBLAGE_PAGE_CONCEPTION_V1_OK")
    print("DocumentEditorView possède maintenant focus_page(numero).")
    print("Le numéro de la page actuellement ouverte est également exposé.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
