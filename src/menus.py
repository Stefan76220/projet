from __future__ import annotations

import tkinter as tk


def creer_menu(fenetre: tk.Tk) -> None:
    """
    Construit la barre de menus principale.
    """

    barre_menu = tk.Menu(fenetre)

    _creer_menu_fichier(barre_menu, fenetre)
    _creer_menu_aide(barre_menu)

    fenetre.config(menu=barre_menu)


# ==========================================================
# Menus
# ==========================================================


def _creer_menu_fichier(
    barre_menu: tk.Menu,
    fenetre: tk.Tk,
) -> None:

    menu = tk.Menu(
        barre_menu,
        tearoff=False,
    )

    menu.add_command(label="Nouveau projet")
    menu.add_command(label="Ouvrir un projet")

    menu.add_separator()

    menu.add_command(
        label="Quitter",
        command=fenetre.quit,
    )

    barre_menu.add_cascade(
        label="Fichier",
        menu=menu,
    )


def _creer_menu_aide(
    barre_menu: tk.Menu,
) -> None:

    menu = tk.Menu(
        barre_menu,
        tearoff=False,
    )

    menu.add_command(
        label="À propos",
    )

    barre_menu.add_cascade(
        label="Aide",
        menu=menu,
    )