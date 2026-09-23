from __future__ import annotations


def main() -> None:
    """Lance la coque V5 sans modifier ni dupliquer l'interface V4 validee."""

    try:
        from src.v4.font_library import register_private_fonts

        register_private_fonts()
    except Exception:
        # Comme en V4, l'audit du Livre signalera les polices manquantes.
        pass

    from src.gui_v5.roman_shell import TomeLineaV5RomanStage

    app = TomeLineaV5RomanStage(
        defer_show=True
    )

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