from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import re
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
MARKER = "OUVERTURE_FENETRE_MAXIMISEE_V1"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def find_target() -> Path:
    candidates: list[Path] = []

    # D'abord les emplacements de code actif usuels.
    roots = [
        PROJECT / "src",
        PROJECT,
    ]

    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("main_window.py"):
            try:
                resolved = path.resolve()
            except Exception:
                resolved = path
            if resolved in seen:
                continue
            seen.add(resolved)

            lowered = {part.lower() for part in path.parts}
            if any(
                blocked in lowered
                for blocked in {
                    "cache",
                    "__pycache__",
                    ".venv",
                    "venv",
                    "backup",
                    "backups",
                }
            ):
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue

            if (
                "class MainWindow" in text
                and "self.root" in text
                and ("geometry(" in text or 'state("zoomed")' in text)
            ):
                candidates.append(path)

    # Priorité au fichier dans src.
    candidates.sort(
        key=lambda p: (
            0 if "src" in {part.lower() for part in p.parts} else 1,
            len(p.parts),
            str(p).lower(),
        )
    )

    if not candidates:
        fail(
            "aucun main_window.py actif contenant class MainWindow "
            "n'a été trouvé dans le projet"
        )

    if len(candidates) > 1:
        print("Fichiers MainWindow trouvés :")
        for candidate in candidates:
            print(f" - {candidate}")
        print(f"Utilisé : {candidates[0]}")

    return candidates[0]


def main() -> None:
    target = find_target()
    original = target.read_text(encoding="utf-8")

    if MARKER in original:
        print("OUVERTURE_MAXIMISEE_DEJA_APPLIQUEE")
        print(f"Fichier : {target}")
        return

    # On ajoute l'état maximisé juste après la géométrie initiale,
    # sans modifier le reste de la fenêtre.
    pattern = re.compile(
        r'(?m)^(?P<indent>\s*)self\.root\.geometry\((?P<args>[^\n]+)\)\s*$'
    )
    matches = list(pattern.finditer(original))

    if len(matches) != 1:
        fail(
            f"la géométrie de la fenêtre principale n'a pas été trouvée "
            f"de manière sûre dans {target}"
        )

    match = matches[0]
    indent = match.group("indent")
    geometry_line = match.group(0)

    replacement = (
        geometry_line
        + "\n"
        + indent
        + f"# {MARKER}\n"
        + indent
        + "# Ouvre PageMaître maximisé tout en gardant la barre Windows.\n"
        + indent
        + "try:\n"
        + indent
        + '    self.root.state("zoomed")\n'
        + indent
        + "except Exception:\n"
        + indent
        + "    pass"
    )

    candidate = (
        original[:match.start()]
        + replacement
        + original[match.end():]
    )

    try:
        compile(candidate, str(target), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"main_window_avant_ouverture_maximisee_{stamp}.py"
    temp = target.with_suffix(".maximisee.tmp")

    try:
        temp.write_text(candidate, encoding="utf-8")
        py_compile.compile(str(temp), doraise=True)
        shutil.copy2(target, backup)
        temp.replace(target)
        py_compile.compile(str(target), doraise=True)
    except Exception as exc:
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass
        if backup.exists():
            shutil.copy2(backup, target)
        fail(f"installation annulée automatiquement : {exc}")

    print("OUVERTURE_MAXIMISEE_OK")
    print(f"Fichier modifié : {target}")
    print("PageMaître s'ouvrira désormais maximisé.")
    print("La barre de titre Windows reste visible.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
