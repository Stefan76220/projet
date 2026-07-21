import tkinter as tk


def creer_menu(fenetre):

    barre_menu = tk.Menu(fenetre)

    menu_fichier = tk.Menu(barre_menu, tearoff=0)
    menu_fichier.add_command(label="Nouveau projet")
    menu_fichier.add_command(label="Ouvrir un projet")
    menu_fichier.add_separator()
    menu_fichier.add_command(label="Quitter", command=fenetre.quit)

    barre_menu.add_cascade(label="Fichier", menu=menu_fichier)

    menu_aide = tk.Menu(barre_menu, tearoff=0)
    menu_aide.add_command(label="À propos")

    barre_menu.add_cascade(label="Aide", menu=menu_aide)

    fenetre.config(menu=barre_menu)