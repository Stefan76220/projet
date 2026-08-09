from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
DOCUMENT_VIEW = PROJECT / "src" / "gui" / "views" / "document_view.py"
WORKSHOP_VIEW = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"

MARKER = "VOYANT_PAGE_OUVERTE_ATELIER_V1"
REQUIRED_ROUTE = "ROUTEUR_CENTRE_MAQUETTAGE_ATELIER_V1"
REQUIRED_WORKSHOP = "def focus_model("

WALL_ANCHOR = "        wall._regulation_bg_photo = None\n"
WALL_INSERT = (
    "        self._regulation_wall = wall\n"
    "        wall._regulation_bg_photo = None\n"
)

BIND_ANCHOR = '        wall.bind("<Configure>", draw_wall, add="+")\n'
BIND_INSERT = (
    "        wall._redraw_regulation = draw_wall\n"
    '        wall.bind("<Configure>", draw_wall, add="+")\n'
)

CLICK_MARKER = "            # CIBLAGE_CENTRE_MAQUETTAGE_V1\n"
INDICATOR = '            # VOYANT_PAGE_OUVERTE_ATELIER_V1\n            # Le voyant décrit un état de session, pas l\'avancement :\n            # il apparaît uniquement si le gabarit associé est réellement\n            # chargé dans l\'Atelier persistant.\n            workshop = self._model_workshop_view\n            active_model_id = (\n                str(getattr(workshop, "active_model_id", "") or "")\n                if workshop is not None\n                else ""\n            )\n            associated_model_id = (\n                self._associated_model_id_for_synoptic_item(item)\n            )\n\n            if (\n                active_model_id\n                and associated_model_id\n                and active_model_id == associated_model_id\n            ):\n                activity_tag = f"{tag}_atelier_active"\n                tab_x1 = x + page_w - 1\n                tab_y1 = y + 31 * scale\n                tab_x2 = x + page_w + 13 * scale\n                tab_y2 = y + 56 * scale\n\n                wall.create_rectangle(\n                    tab_x1,\n                    tab_y1,\n                    tab_x2,\n                    tab_y2,\n                    fill=self.ATELIER,\n                    outline="#FFFFFF",\n                    width=1,\n                    tags=(activity_tag,),\n                )\n                wall.create_text(\n                    (tab_x1 + tab_x2) / 2,\n                    (tab_y1 + tab_y2) / 2,\n                    text="A",\n                    fill="#FFFFFF",\n                    font=(\n                        Fonts.FAMILY,\n                        max(7, int(8 * scale)),\n                        "bold",\n                    ),\n                    anchor="center",\n                    tags=(activity_tag,),\n                )\n\n                def show_atelier_activity_tip(event) -> None:\n                    wall.delete("atelier_activity_tooltip")\n                    cx = wall.canvasx(event.x) + 14\n                    cy = wall.canvasy(event.y) - 12\n\n                    text_id = wall.create_text(\n                        cx,\n                        cy,\n                        text="Atelier · gabarit actuellement ouvert",\n                        fill=self.INK,\n                        font=(Fonts.FAMILY, 8, "bold"),\n                        anchor="sw",\n                        tags=("atelier_activity_tooltip",),\n                    )\n                    bbox = wall.bbox(text_id)\n                    if bbox is None:\n                        return\n\n                    x1, y1, x2, y2 = bbox\n                    bubble = wall.create_rectangle(\n                        x1 - 8,\n                        y1 - 5,\n                        x2 + 8,\n                        y2 + 5,\n                        fill="#FFFDFC",\n                        outline=self.ATELIER,\n                        width=1,\n                        tags=("atelier_activity_tooltip",),\n                    )\n                    wall.tag_lower(bubble, text_id)\n\n                def hide_atelier_activity_tip(_event=None) -> None:\n                    wall.delete("atelier_activity_tooltip")\n\n                wall.tag_bind(\n                    activity_tag,\n                    "<Enter>",\n                    show_atelier_activity_tip,\n                )\n                wall.tag_bind(\n                    activity_tag,\n                    "<Leave>",\n                    hide_atelier_activity_tip,\n                )\n                wall.tag_bind(\n                    activity_tag,\n                    "<Button-1>",\n                    lambda _evt, current_item=item: self._route_synoptic_page(\n                        current_item\n                    ),\n                )\n\n'

OLD_CLOSE = """    def _close_model_workshop(self) -> None:
        \"\"\"Revient au Centre sans reconstruire les deux espaces.\"\"\"

        view = self._model_workshop_view
        if view is not None:
            view.hide()
        self._restore_project_tools_after_subspace()
"""

NEW_CLOSE = """    def _close_model_workshop(self) -> None:
        \"\"\"Revient au Centre sans reconstruire les deux espaces.\"\"\"

        view = self._model_workshop_view
        if view is not None:
            view.hide()
        self._restore_project_tools_after_subspace()

        # Le Centre existe déjà derrière l'Atelier : on ne le reconstruit pas.
        # On redessine seulement son Canvas afin que l'état "gabarit ouvert"
        # soit immédiatement visible au retour.
        wall = getattr(self, "_regulation_wall", None)
        if wall is not None:
            try:
                if wall.winfo_exists():
                    redraw = getattr(
                        wall,
                        "_redraw_regulation",
                        None,
                    )
                    if callable(redraw):
                        wall.after_idle(redraw)
            except tk.TclError:
                pass
"""


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not DOCUMENT_VIEW.is_file():
        fail(f"fichier introuvable : {DOCUMENT_VIEW}")
    if not WORKSHOP_VIEW.is_file():
        fail(f"fichier introuvable : {WORKSHOP_VIEW}")

    source = DOCUMENT_VIEW.read_text(encoding="utf-8")
    workshop_source = WORKSHOP_VIEW.read_text(encoding="utf-8")

    if MARKER in source:
        print("VOYANT_PAGE_OUVERTE_ATELIER_V1_DEJA_APPLIQUE")
        return

    if REQUIRED_ROUTE not in source:
        fail("le routeur Centre -> Atelier n'est pas détecté")

    if REQUIRED_WORKSHOP not in workshop_source:
        fail("le ciblage direct des gabarits Atelier n'est pas détecté")

    if "def active_model_id" not in workshop_source:
        fail("active_model_id n'est pas disponible dans l'Atelier")

    candidate = source

    if WALL_ANCHOR not in candidate:
        fail("Canvas du synoptique introuvable")
    candidate = candidate.replace(
        WALL_ANCHOR,
        WALL_INSERT,
        1,
    )

    if BIND_ANCHOR not in candidate:
        fail("liaison de redessin du synoptique introuvable")
    candidate = candidate.replace(
        BIND_ANCHOR,
        BIND_INSERT,
        1,
    )

    if CLICK_MARKER not in candidate:
        fail("point d'insertion du voyant près du clic page introuvable")
    candidate = candidate.replace(
        CLICK_MARKER,
        INDICATOR + CLICK_MARKER,
        1,
    )

    if OLD_CLOSE not in candidate:
        fail("méthode de retour Atelier -> Centre inattendue")
    candidate = candidate.replace(
        OLD_CLOSE,
        NEW_CLOSE,
        1,
    )

    try:
        compile(candidate, str(DOCUMENT_VIEW), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_voyant_atelier_{stamp}.py"
    )
    temp = DOCUMENT_VIEW.with_suffix(".voyant_atelier.tmp")

    try:
        temp.write_text(candidate, encoding="utf-8")
        py_compile.compile(str(temp), doraise=True)

        shutil.copy2(DOCUMENT_VIEW, backup)
        temp.replace(DOCUMENT_VIEW)

        py_compile.compile(str(DOCUMENT_VIEW), doraise=True)

    except Exception as exc:
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass

        if backup.exists():
            shutil.copy2(backup, DOCUMENT_VIEW)

        fail(f"installation annulée automatiquement : {exc}")

    print("VOYANT_PAGE_OUVERTE_ATELIER_V1_OK")
    print("Un petit onglet vert A signale un gabarit actuellement chargé dans Atelier.")
    print("Le survol explique : Atelier · gabarit actuellement ouvert.")
    print("Le voyant est recalculé au retour de l'Atelier sans reconstruire le Centre.")
    print("Un clic sur l'onglet utilise le même routeur que la vignette.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
