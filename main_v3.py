from __future__ import annotations


def main() -> None:
    # La fenêtre de préparation reste ouverte jusqu'à ce que le VRAI moteur
    # du Visionneur, son WebView2 et son rendu Three.js aient été préchauffés.
    preparation = None
    try:
        from src.gui_v3.startup_runtime import prepare_before_launch

        preparation = prepare_before_launch(keep_window=True)
    except Exception:
        # Une défaillance du Visionneur ne doit jamais empêcher TomeLinea de
        # démarrer. Le bouton Visionneur présentera le diagnostic si besoin.
        preparation = None

    from src.gui_v3.app import TomeLineaV3

    progress = getattr(preparation, "update", None)
    try:
        app = TomeLineaV3(startup_progress=progress if callable(progress) else None)
    finally:
        close = getattr(preparation, "close", None)
        if callable(close):
            close()

    app.mainloop()


if __name__ == "__main__":
    main()
