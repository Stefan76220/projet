from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"
MARKER = "BANDEAU_NAVIGATION_PERMANENT_V1"

EXPECTED = {'show': 'f9ad77ef9c7462d6a11f7bff722e963fc4bf88cdc1832b7d8f445a067f7570db', '_create_header': '36bc168063c2a064cec4f77a5fa8bd34381aade4e0578fa4b19ddb516d958a74'}
NEW_SHOW = '    def show(self) -> None:\n        self.pages = self._load_project_pages()\n\n        # BANDEAU_NAVIGATION_PERMANENT_V1\n        # Le Centre est entièrement construit hors affichage. Le bandeau\n        # PageMaître est désormais la première zone de toutes les pages\n        # productives ; ici, il est posé avant le bandeau fonctionnel existant.\n        root = ctk.CTkFrame(\n            self.parent,\n            fg_color=self.WINDOW_BG,\n            corner_radius=0,\n        )\n        root.grid_columnconfigure(0, weight=1)\n        root.grid_rowconfigure(3, weight=1)\n\n        navigation = self._create_internal_navigation_ribbon(root)\n        navigation.grid(\n            row=0,\n            column=0,\n            sticky="ew",\n            padx=10,\n            pady=(5, 2),\n        )\n\n        header = self._create_header(root)\n        header.grid(\n            row=1,\n            column=0,\n            sticky="ew",\n            padx=10,\n            pady=(0, 2),\n        )\n\n        # Le ruban fonctionnel du Centre reste volontairement inchangé pour\n        # cette première validation : on juge d\'abord uniquement le nouveau\n        # bandeau permanent.\n        workspace_bar = self._create_workspace_bar(root)\n        workspace_bar.grid(\n            row=2,\n            column=0,\n            sticky="ew",\n            padx=10,\n            pady=(0, 5),\n        )\n\n        main_workspace = self._create_main_workspace(root)\n        main_workspace.grid(\n            row=3,\n            column=0,\n            sticky="nsew",\n            padx=10,\n            pady=(0, 8),\n        )\n\n        root.update_idletasks()\n        root.pack(fill="both", expand=True)\n        root.lift()\n'
NEW_NAV = '    def _create_internal_navigation_ribbon(\n        self,\n        parent,\n    ) -> ctk.CTkFrame:\n        """Bandeau permanent de navigation interne PageMaître.\n\n        Structure figée :\n        - gauche : Visualisation, Suivi du livre ;\n        - centre : parcours des bureaux ;\n        - droite : Fermer.\n        """\n        ribbon = ctk.CTkFrame(\n            parent,\n            height=62,\n            fg_color=self.RIBBON_BG,\n            corner_radius=9,\n            border_width=1,\n            border_color=self.BORDER,\n        )\n        ribbon.grid_propagate(False)\n        ribbon.grid_columnconfigure(0, weight=0, minsize=244)\n        ribbon.grid_columnconfigure(1, weight=1)\n        ribbon.grid_columnconfigure(2, weight=0, minsize=92)\n        ribbon.grid_rowconfigure(0, weight=1)\n\n        # Décor léger PageMaître sur toute la surface du bandeau.\n        background_path = (\n            Path(__file__).resolve().parents[3]\n            / "assets"\n            / "interface"\n            / "backgrounds"\n            / "editorial_bg_soft.png"\n        )\n        if background_path.is_file():\n            try:\n                from PIL import Image, ImageTk\n\n                source = Image.open(background_path).convert("RGB")\n                label = tk.Label(\n                    ribbon,\n                    borderwidth=0,\n                    highlightthickness=0,\n                    background=self.RIBBON_BG,\n                    takefocus=False,\n                )\n                label.place(x=0, y=0, relwidth=1, relheight=1)\n                label.lower()\n\n                ribbon._navigation_bg_source = source\n                ribbon._navigation_bg_photo = None\n                ribbon._navigation_bg_label = label\n\n                def redraw_background(_event=None) -> None:\n                    try:\n                        width = max(1, int(ribbon.winfo_width()))\n                        height = max(1, int(ribbon.winfo_height()))\n                        if width <= 2 or height <= 2:\n                            return\n\n                        source_ratio = source.width / source.height\n                        target_ratio = width / height\n                        if target_ratio > source_ratio:\n                            resize_width = width\n                            resize_height = max(\n                                height,\n                                int(round(width / source_ratio)),\n                            )\n                        else:\n                            resize_height = height\n                            resize_width = max(\n                                width,\n                                int(round(height * source_ratio)),\n                            )\n\n                        resized = source.resize(\n                            (resize_width, resize_height),\n                            Image.Resampling.LANCZOS,\n                        )\n                        left = max(0, (resize_width - width) // 2)\n                        top = max(0, (resize_height - height) // 2)\n                        cropped = resized.crop(\n                            (left, top, left + width, top + height)\n                        )\n                        photo = ImageTk.PhotoImage(cropped)\n                        ribbon._navigation_bg_photo = photo\n                        label.configure(image=photo)\n                        label.lower()\n                    except Exception:\n                        pass\n\n                ribbon.bind("<Configure>", redraw_background, add="+")\n                ribbon.after_idle(redraw_background)\n            except Exception:\n                pass\n\n        left = ctk.CTkFrame(\n            ribbon,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        left.grid(\n            row=0,\n            column=0,\n            sticky="w",\n            padx=(8, 4),\n            pady=8,\n        )\n\n        centre = ctk.CTkFrame(\n            ribbon,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        centre.grid(\n            row=0,\n            column=1,\n            sticky="nsew",\n            padx=2,\n            pady=8,\n        )\n\n        right = ctk.CTkFrame(\n            ribbon,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        right.grid(\n            row=0,\n            column=2,\n            sticky="e",\n            padx=(4, 8),\n            pady=8,\n        )\n\n        def button(\n            host,\n            *,\n            text: str,\n            width: int,\n            color: str,\n            soft: str,\n            command=None,\n            active: bool = False,\n            enabled: bool = True,\n        ) -> ctk.CTkButton:\n            if active:\n                fg = self.NAVY\n                hover = self.NAVY\n                text_color = "#FFFFFF"\n                border = self.NAVY\n                state = "normal"\n                callback = command or (lambda: None)\n            elif enabled and callable(command):\n                fg = soft\n                hover = self._hover_color(soft)\n                text_color = color\n                border = color\n                state = "normal"\n                callback = command\n            else:\n                fg = "#F0F2F4"\n                hover = "#F0F2F4"\n                text_color = self.TEXT_LIGHT\n                border = "#D9DDE2"\n                state = "disabled"\n                callback = None\n\n            return ctk.CTkButton(\n                host,\n                text=text,\n                width=width,\n                height=38,\n                corner_radius=7,\n                fg_color=fg,\n                hover_color=hover,\n                text_color=text_color,\n                border_width=1,\n                border_color=border,\n                font=(Fonts.FAMILY, 9, "bold" if active else "normal"),\n                state=state,\n                command=callback,\n            )\n\n        # Outils permanents : présents dès maintenant à leur place définitive.\n        # Leurs fenêtres dédiées seront branchées lorsqu\'elles seront construites.\n        button(\n            left,\n            text="▣  Visualisation",\n            width=112,\n            color=self.SKY,\n            soft=self.MAQUETTAGE_SOFT,\n            enabled=False,\n        ).pack(side="left", padx=(0, 4))\n\n        button(\n            left,\n            text="◎  Suivi du livre",\n            width=116,\n            color=self.CELADON,\n            soft=self.ATELIER_SOFT,\n            enabled=False,\n        ).pack(side="left")\n\n        steps = (\n            (\n                "Centre",\n                70,\n                self.NAVY,\n                "#E7EEF6",\n                None,\n                True,\n                True,\n            ),\n            (\n                "Maquettage",\n                86,\n                self.MAQUETTAGE,\n                self.MAQUETTAGE_SOFT,\n                self._open_mockup,\n                False,\n                True,\n            ),\n            (\n                "Atelier",\n                68,\n                self.ATELIER,\n                self.ATELIER_SOFT,\n                self._open_model_workshop,\n                False,\n                True,\n            ),\n            (\n                "Conception",\n                84,\n                self.CONCEPTION,\n                self.CONCEPTION_SOFT,\n                self._open_atelier,\n                False,\n                True,\n            ),\n            (\n                "Assemblage",\n                84,\n                self.ASSEMBLAGE,\n                self.ASSEMBLAGE_SOFT,\n                None,\n                False,\n                False,\n            ),\n            (\n                "Vérification",\n                88,\n                self.VERIFICATION,\n                self.VERIFICATION_SOFT,\n                None,\n                False,\n                False,\n            ),\n            (\n                "Finalisation",\n                84,\n                self.FINALISATION,\n                self.FINALISATION_SOFT,\n                None,\n                False,\n                False,\n            ),\n        )\n\n        flow = ctk.CTkFrame(\n            centre,\n            fg_color="transparent",\n            corner_radius=0,\n        )\n        flow.pack(expand=True)\n\n        for index, (\n            title,\n            width,\n            color,\n            soft,\n            command,\n            active,\n            enabled,\n        ) in enumerate(steps):\n            button(\n                flow,\n                text=title,\n                width=width,\n                color=color,\n                soft=soft,\n                command=command,\n                active=active,\n                enabled=enabled,\n            ).pack(\n                side="left",\n                padx=(0 if index == 0 else 2, 0),\n            )\n\n        # Fermer signifie fermer le Centre et revenir à l\'accueil de PageMaître.\n        close_button = ctk.CTkButton(\n            right,\n            text="×  Fermer",\n            width=78,\n            height=38,\n            corner_radius=7,\n            fg_color=self.FINALISATION_SOFT,\n            hover_color=self._hover_color(self.FINALISATION_SOFT),\n            text_color=self.CORAL,\n            border_width=1,\n            border_color=self.CORAL,\n            font=(Fonts.FAMILY, 9, "bold"),\n            command=self._return_home,\n        )\n        close_button.pack()\n\n        return ribbon\n'
NEW_HEADER = '    def _create_header(self, parent) -> ctk.CTkFrame:\n        """Contexte du Centre, sous le bandeau permanent."""\n        frame = ctk.CTkFrame(\n            parent,\n            fg_color="transparent",\n            height=30,\n        )\n        frame.grid_columnconfigure(0, weight=1)\n        frame.grid_propagate(False)\n\n        ctk.CTkLabel(\n            frame,\n            text="Centre du projet",\n            font=Fonts.H2,\n            text_color=self.INK,\n        ).grid(row=0, column=0, sticky="w")\n\n        project_name = str(\n            getattr(self.project, "name", "")\n            or "Projet sans nom"\n        )\n\n        project_type = str(\n            getattr(\n                self.project,\n                "project_type",\n                "ouvrage_structure",\n            )\n            or "ouvrage_structure"\n        )\n        appearance = self.PROJECT_TYPE_APPEARANCES.get(\n            project_type,\n            self.PROJECT_TYPE_APPEARANCES["ouvrage_structure"],\n        )\n\n        badge = ctk.CTkLabel(\n            frame,\n            text=appearance["label"],\n            height=22,\n            corner_radius=11,\n            fg_color=appearance["soft"],\n            text_color=appearance["color"],\n            border_width=1,\n            border_color=appearance["color"],\n            font=(Fonts.FAMILY, 8, "bold"),\n            padx=9,\n        )\n        badge.grid(row=0, column=1, sticky="e", padx=(12, 8))\n\n        ctk.CTkLabel(\n            frame,\n            text=project_name,\n            font=Fonts.SMALL,\n            text_color=self.TEXT_MUTED,\n        ).grid(row=0, column=2, sticky="e", padx=(0, 2))\n\n        return frame\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def get_method(source: str, name: str) -> str:
    lines = source.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.startswith(f"    def {name}("):
            start = i
            break
    if start is None:
        fail(f"méthode {name} introuvable")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("    def ") or lines[i].startswith("    @"):
            end = i
            break
    return "".join(lines[start:end])


def replace_method(source: str, name: str, block: str) -> str:
    old = get_method(source, name)
    return source.replace(old, block.rstrip() + "\n\n", 1)


def digest(block: str) -> str:
    return hashlib.sha256(block.encode("utf-8")).hexdigest()


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("BANDEAU_NAVIGATION_PERMANENT_DEJA_APPLIQUE")
        return

    for method_name, expected_hash in EXPECTED.items():
        if digest(get_method(original, method_name)) != expected_hash:
            fail(
                f"la méthode {method_name} a changé depuis le fichier transmis. "
                "Le correctif s'arrête par sécurité."
            )

    candidate = replace_method(original, "show", NEW_SHOW)

    old_header = get_method(candidate, "_create_header")
    candidate = candidate.replace(
        old_header,
        NEW_NAV.rstrip() + "\n\n" + NEW_HEADER.rstrip() + "\n\n",
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
        / f"document_view_avant_bandeau_navigation_{stamp}.py"
    )
    temp = TARGET.with_suffix(".navigation.tmp")

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

    print("BANDEAU_NAVIGATION_PERMANENT_V1_OK")
    print("Gauche : Visualisation | Suivi du livre.")
    print("Centre : Centre | Maquettage | Atelier | Conception | Assemblage | Vérification | Finalisation.")
    print("Droite : × Fermer.")
    print("Centre actif ; Maquettage, Atelier et Conception accessibles.")
    print("Étapes futures visibles mais désactivées.")
    print("Le ruban fonctionnel existant dessous est volontairement conservé pour cette première validation.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
