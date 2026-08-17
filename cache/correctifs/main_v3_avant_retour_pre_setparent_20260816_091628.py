from __future__ import annotations

import sys

from src.gui_v3.app import TomeLineaV3


def main() -> None:
    if sys.platform == "win32":
        from src.gui_v3.native_host import run_native_tomelinea

        run_native_tomelinea(TomeLineaV3)
        return

    app = TomeLineaV3()
    app.mainloop()


if __name__ == "__main__":
    main()
