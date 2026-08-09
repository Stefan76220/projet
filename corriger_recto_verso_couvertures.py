from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"


def stop(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\n"
        "Aucun fichier n'a été modifié."
    )


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if new in source:
        return source
    if old not in source:
        stop(f"bloc introuvable : {label}")
    return source.replace(old, new, 1)


def main() -> None:
    if not TARGET.is_file():
        stop(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")
    source = original

    # 1. Types de couvertures proposés dans les règles recto-verso.
    old = """    def _eligible_recto_verso_types(self) -> list[dict[str, Any]]:
        # La quatrième peut recevoir une page blanche avant le bloc de fin.
        # Les autres pages structurelles restent exclues pour préserver leurs
        # positions verrouillées.
        excluded = {
            "couverture",
            "deuxieme_couverture",
            "troisieme_couverture",
            "page_blanche",
        }
        return [
            definition
            for definition in self._page_types()
            if str(definition.get("type", "")) not in excluded
        ]
"""
    new = """    def _eligible_recto_verso_types(self) -> list[dict[str, Any]]:
        # Couvertures et règles autorisées :
        # - 2e de couverture : blanc après uniquement ;
        # - 3e de couverture : blanc avant uniquement ;
        # - 4e de couverture : blanc avant uniquement.
        # La couverture reste exclue.
        excluded = {
            "couverture",
            "page_blanche",
        }
        return [
            definition
            for definition in self._page_types()
            if str(definition.get("type", "")) not in excluded
        ]
"""
    source = replace_once(source, old, new, "types éligibles")

    # 2. Libellés explicites dans la fenêtre Recto-verso.
    old = """                checkbox_text = str(definition.get("title", "Page"))
                if page_type == "quatrieme":
                    checkbox_text += " — avant uniquement"
"""
    new = """                checkbox_text = str(definition.get("title", "Page"))
                if page_type == "deuxieme_couverture":
                    checkbox_text += " — après uniquement"
                elif page_type in {"troisieme_couverture", "quatrieme"}:
                    checkbox_text += " — avant uniquement"
"""
    source = replace_once(source, old, new, "libellés des couvertures")

    # 3. Active/désactive les couvertures selon Avant / Après.
    old = """        def update_position_constraints(*_args: Any) -> None:
            fourth_var = type_vars.get("quatrieme")
            fourth_check = type_checks.get("quatrieme")
            if fourth_var is None or fourth_check is None:
                return
            if position_var.get() == "after":
                fourth_var.set(False)
                fourth_check.configure(state="disabled")
            else:
                fourth_check.configure(state="normal")

        position_var.trace_add("write", update_position_constraints)
        update_position_constraints()
"""
    new = """        def update_position_constraints(*_args: Any) -> None:
            position = position_var.get()
            restrictions = {
                "deuxieme_couverture": "after",
                "troisieme_couverture": "before",
                "quatrieme": "before",
            }
            for page_type, allowed_position in restrictions.items():
                variable = type_vars.get(page_type)
                checkbox = type_checks.get(page_type)
                if variable is None or checkbox is None:
                    continue
                if position != allowed_position:
                    variable.set(False)
                    checkbox.configure(state="disabled")
                else:
                    checkbox.configure(state="normal")

        position_var.trace_add("write", update_position_constraints)
        update_position_constraints()
"""
    source = replace_once(source, old, new, "contraintes Avant/Après")

    # 4. Sécurité supplémentaire à l'enregistrement.
    old = """            position = position_var.get()
            if position == "after" and "quatrieme" in selected:
                status_label.configure(
                    text=(
                        "La quatrième de couverture accepte uniquement "
                        "une page blanche avant."
                    )
                )
                return
            editing_id = self._recto_rule_editor_id
"""
    new = """            position = position_var.get()
            invalid = (
                (
                    position == "before"
                    and "deuxieme_couverture" in selected
                )
                or (
                    position == "after"
                    and (
                        "troisieme_couverture" in selected
                        or "quatrieme" in selected
                    )
                )
            )
            if invalid:
                status_label.configure(
                    text=(
                        "Position non autorisée : "
                        "2e = après uniquement ; "
                        "3e et 4e = avant uniquement."
                    )
                )
                return
            editing_id = self._recto_rule_editor_id
"""
    source = replace_once(source, old, new, "validation de la règle")

    # 5. Normalisation des règles enregistrées/importées.
    old = """                key = (position, page_type)
                if page_type == "quatrieme" and position == "after":
                    continue
                if page_type in eligible and key not in occupied:
"""
    new = """                key = (position, page_type)
                if (
                    page_type == "deuxieme_couverture"
                    and position != "after"
                ):
                    continue
                if (
                    page_type in {"troisieme_couverture", "quatrieme"}
                    and position != "before"
                ):
                    continue
                if page_type in eligible and key not in occupied:
"""
    source = replace_once(source, old, new, "normalisation des règles")

    # 6. Sécurité de calcul, même en présence d'anciennes données incohérentes.
    old = """        # La quatrième est une borne finale : une consigne « après » serait
        # incohérente et est donc toujours neutralisée.
        after_types.discard("quatrieme")
        return before_types, after_types
"""
    new = """        # Sécurité structurelle des couvertures.
        before_types.discard("deuxieme_couverture")
        after_types.discard("troisieme_couverture")
        after_types.discard("quatrieme")
        return before_types, after_types
"""
    source = replace_once(source, old, new, "sécurité de calcul")

    # 7. Contrôle silencieux des éventuelles anciennes règles impossibles.
    old = """                elif page_type == "quatrieme" and position == "after":
                    add(
                        "error",
                        "Règle impossible après la quatrième",
                        "La quatrième étant la dernière page, seul un blanc avant est autorisé.",
                    )
"""
    new = """                elif (
                    page_type == "deuxieme_couverture"
                    and position == "before"
                ):
                    add(
                        "error",
                        "Règle impossible avant la deuxième",
                        "La deuxième de couverture accepte uniquement un blanc après.",
                    )
                elif (
                    page_type == "troisieme_couverture"
                    and position == "after"
                ):
                    add(
                        "error",
                        "Règle impossible après la troisième",
                        "La troisième de couverture accepte uniquement un blanc avant.",
                    )
                elif page_type == "quatrieme" and position == "after":
                    add(
                        "error",
                        "Règle impossible après la quatrième",
                        "La quatrième étant la dernière page, seul un blanc avant est autorisé.",
                    )
"""
    source = replace_once(source, old, new, "contrôle de structure")

    if source == original:
        print("RECTO_VERSO_COUVERTURES_DEJA_CORRECT")
        return

    # Validation syntaxique avant écriture.
    compile(source, str(TARGET), "exec")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"mockup_view_avant_recto_couvertures_{stamp}.py"
    )
    shutil.copy2(TARGET, backup)

    try:
        TARGET.write_text(source, encoding="utf-8")
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        shutil.copy2(backup, TARGET)
        stop(f"correction annulée automatiquement : {exc}")

    pycache = TARGET.parent / "__pycache__"
    if pycache.exists():
        shutil.rmtree(pycache, ignore_errors=True)

    print("RECTO_VERSO_COUVERTURES_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("2e couverture : blanc après uniquement.")
    print("3e couverture : blanc avant uniquement.")
    print("4e couverture : blanc avant uniquement.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
