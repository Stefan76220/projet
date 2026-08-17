from __future__ import annotations

"""Petite couche Win32 SANS callback Python.

Ce module n'intercepte aucun WndProc. Toutes les opérations sont des appels
synchrones initiés par Tk : résolution du HWND, bouton de barre des tâches,
minimisation et suspension temporaire du redraw pendant un changement de
geometry.

But : conserver l'habillage ``overrideredirect`` de TomeLinea sans réintroduire
le crash GIL observé avec un callback ctypes WNDPROC sous Python 3.13.
"""

import sys
from contextlib import contextmanager


class WindowsSafeOps:
    def __init__(self, root) -> None:
        self.root = root
        self.available = sys.platform == "win32"
        self.hwnd = None
        if self.available:
            self._init_api()

    def _init_api(self) -> None:
        import ctypes
        from ctypes import wintypes

        self.ctypes = ctypes
        self.wintypes = wintypes
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)

        self.HWND = wintypes.HWND
        self.LONG_PTR = ctypes.c_ssize_t
        self.WPARAM = ctypes.c_size_t
        self.LPARAM = ctypes.c_ssize_t

        self.user32.GetAncestor.argtypes = [self.HWND, wintypes.UINT]
        self.user32.GetAncestor.restype = self.HWND
        self.user32.GetParent.argtypes = [self.HWND]
        self.user32.GetParent.restype = self.HWND
        self.user32.GetWindowLongPtrW.argtypes = [self.HWND, ctypes.c_int]
        self.user32.GetWindowLongPtrW.restype = self.LONG_PTR
        self.user32.SetWindowLongPtrW.argtypes = [self.HWND, ctypes.c_int, self.LONG_PTR]
        self.user32.SetWindowLongPtrW.restype = self.LONG_PTR
        self.user32.SetWindowPos.argtypes = [
            self.HWND,
            self.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.UINT,
        ]
        self.user32.SetWindowPos.restype = wintypes.BOOL
        self.user32.ShowWindow.argtypes = [self.HWND, ctypes.c_int]
        self.user32.ShowWindow.restype = wintypes.BOOL
        self.user32.SendMessageW.argtypes = [
            self.HWND,
            wintypes.UINT,
            self.WPARAM,
            self.LPARAM,
        ]
        self.user32.SendMessageW.restype = self.LONG_PTR
        self.user32.RedrawWindow.argtypes = [
            self.HWND,
            ctypes.c_void_p,
            wintypes.HRGN,
            wintypes.UINT,
        ]
        self.user32.RedrawWindow.restype = wintypes.BOOL

    def resolve(self):
        if not self.available:
            return None
        try:
            self.root.update_idletasks()
            hwnd = None
            # ``wm frame`` est l'API Tk prévue pour obtenir le wrapper externe
            # d'un toplevel. Sur Windows la valeur est généralement hexadécimale.
            try:
                frame_id = self.root.tk.call("wm", "frame", self.root._w)
                text = str(frame_id).strip()
                if text:
                    hwnd = self.HWND(int(text, 0))
            except Exception:
                hwnd = None

            if not hwnd:
                child = self.HWND(int(self.root.winfo_id()))
                hwnd = self.user32.GetAncestor(child, 2)  # GA_ROOT
                if not hwnd:
                    hwnd = self.user32.GetParent(child) or child
            self.hwnd = hwnd
            return hwnd
        except Exception:
            self.hwnd = None
            return None

    def ensure_taskbar_button(self) -> bool:
        """Force le wrapper override-redirect à se comporter comme une app.

        Tk donne normalement WS_EX_TOOLWINDOW aux fenêtres override-redirect.
        On remplace uniquement cet indicateur par WS_EX_APPWINDOW. Aucun
        WndProc n'est installé ni remplacé.
        """
        hwnd = self.hwnd or self.resolve()
        if not hwnd:
            return False
        try:
            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW = 0x00040000
            exstyle = int(self.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE))
            wanted = (exstyle & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            if wanted != exstyle:
                self.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, self.LONG_PTR(wanted))
                SWP_NOSIZE = 0x0001
                SWP_NOMOVE = 0x0002
                SWP_NOZORDER = 0x0004
                SWP_NOACTIVATE = 0x0010
                SWP_FRAMECHANGED = 0x0020
                self.user32.SetWindowPos(
                    hwnd,
                    self.HWND(0),
                    0,
                    0,
                    0,
                    0,
                    SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
                )
            return True
        except Exception:
            return False

    @contextmanager
    def redraw_suspended(self):
        """Gèle seulement la peinture native pendant le recalcul Tk."""
        hwnd = self.hwnd or self.resolve()
        if not hwnd:
            yield
            return

        WM_SETREDRAW = 0x000B
        RDW_INVALIDATE = 0x0001
        RDW_ERASE = 0x0004
        RDW_ALLCHILDREN = 0x0080
        RDW_UPDATENOW = 0x0100
        RDW_FRAME = 0x0400

        disabled = False
        try:
            self.user32.SendMessageW(hwnd, WM_SETREDRAW, 0, 0)
            disabled = True
            yield
        finally:
            if disabled:
                try:
                    self.user32.SendMessageW(hwnd, WM_SETREDRAW, 1, 0)
                    self.user32.RedrawWindow(
                        hwnd,
                        None,
                        None,
                        RDW_INVALIDATE | RDW_ERASE | RDW_FRAME | RDW_ALLCHILDREN | RDW_UPDATENOW,
                    )
                except Exception:
                    pass

    def minimize(self) -> bool:
        hwnd = self.hwnd or self.resolve()
        if not hwnd:
            return False
        try:
            self.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
            return True
        except Exception:
            return False

    def restore(self) -> bool:
        hwnd = self.hwnd or self.resolve()
        if not hwnd:
            return False
        try:
            self.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            return True
        except Exception:
            return False
