from __future__ import annotations


def main() -> None:
    # La préparation est volontairement exécutée AVANT la création de la
    # fenêtre principale : moteurs locaux, ressources 3D et WebView2 sont
    # vérifiés dans la petite fenêtre de lancement TomeLinea.
    try:
        from src.gui_v3.startup_runtime import prepare_before_launch

        prepare_before_launch()
    except Exception:
        # Une défaillance du Visionneur ne doit jamais empêcher TomeLinea de
        # démarrer. Le bouton Visionneur présentera le diagnostic si besoin.
        pass

    from src.gui_v3.app import TomeLineaV3

    app = TomeLineaV3()
    app.mainloop()


if __name__ == "__main__":
    main()
