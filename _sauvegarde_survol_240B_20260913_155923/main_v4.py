from __future__ import annotations


def main() -> None:
    # Charge d'abord les polices privées TomeLinea. Elles deviennent
    # disponibles uniquement pour ce processus : aucune installation Windows
    # globale et aucun redémarrage du système ne sont nécessaires.
    try:
        from src.v4.font_library import register_private_fonts

        register_private_fonts()
    except Exception:
        # Une bibliothèque incomplète ne doit jamais empêcher l'ouverture :
        # l'audit du livre signalera ensuite les polices réellement manquantes.
        pass

    # Le lancement initial ne crée plus de processus/fenêtre d'attente
    # séparé : sous Windows, ce second processus provoquait des flashes
    # visibles avant TomeLinea. La V4 se construit entièrement cachée,
    # puis est affichée une seule fois lorsqu'elle est prête.
    #
    # Phase 2.39G : Format → règles Texte → Survol adaptatif.
    from src.gui_v4.survol_shell import TomeLineaV4Survol

    app = TomeLineaV4Survol(defer_show=True)

    try:
        app.show_prepared_window()
    except Exception:
        try:
            app.deiconify()
            app.lift()
        except Exception:
            pass

    app.mainloop()


if __name__ == "__main__":
    main()
