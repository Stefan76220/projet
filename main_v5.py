from __future__ import annotations


def main() -> None:
    """Lance la nouvelle chaîne séquentielle TomeLinea V5."""

    try:
        from src.v4.font_library import register_private_fonts
        register_private_fonts()
    except Exception:
        pass

    from src.gui_v5.sequential_shell import TomeLineaV5SequentialShell

    app = TomeLineaV5SequentialShell()
    app.mainloop()


if __name__ == "__main__":
    main()