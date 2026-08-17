from __future__ import annotations

import sys
from typing import Callable


class WindowsNativeFrame:
    """Cadre Windows natif avec zone cliente intégrale.

    Sous Windows, la fenêtre reste une vraie fenêtre WS_OVERLAPPEDWINDOW :
    réduction, restauration, Alt+Tab, barre des tâches et maximisation restent
    gérées par Windows. Seul le cadre non-client standard est supprimé via
    WM_NCCALCSIZE afin que TomeLinea dessine son propre bandeau.

    Hors Windows, les méthodes retombent sur les commandes Tk standard.
    """

    def __init__(self, root) -> None:
        self.root = root
        self.available = sys.platform == "win32"
        self.installed = False
        self.hwnd = None
        self._old_wndproc = None
        self._wndproc_callback = None
        self._button_state_callback: Callable[[bool], None] | None = None

        if self.available:
            self._init_win32()

    def _init_win32(self) -> None:
        import ctypes
        from ctypes import wintypes

        self.ctypes = ctypes
        self.wintypes = wintypes
        self.user32 = ctypes.windll.user32

        self.LRESULT = ctypes.c_ssize_t
        self.LONG_PTR = ctypes.c_ssize_t
        self.WPARAM = ctypes.c_size_t
        self.LPARAM = ctypes.c_ssize_t
        self.HWND = wintypes.HWND
        self.UINT = wintypes.UINT

        self.WNDPROC = ctypes.WINFUNCTYPE(
            self.LRESULT,
            self.HWND,
            self.UINT,
            self.WPARAM,
            self.LPARAM,
        )

        self.user32.GetAncestor.argtypes = [self.HWND, wintypes.UINT]
        self.user32.GetAncestor.restype = self.HWND

        self.user32.GetParent.argtypes = [self.HWND]
        self.user32.GetParent.restype = self.HWND

        self.user32.SetWindowLongPtrW.argtypes = [self.HWND, ctypes.c_int, self.LONG_PTR]
        self.user32.SetWindowLongPtrW.restype = self.LONG_PTR

        self.user32.CallWindowProcW.argtypes = [
            self.LONG_PTR,
            self.HWND,
            self.UINT,
            self.WPARAM,
            self.LPARAM,
        ]
        self.user32.CallWindowProcW.restype = self.LRESULT

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

        self.user32.IsZoomed.argtypes = [self.HWND]
        self.user32.IsZoomed.restype = wintypes.BOOL

        self.user32.PostMessageW.argtypes = [self.HWND, wintypes.UINT, self.WPARAM, self.LPARAM]
        self.user32.PostMessageW.restype = wintypes.BOOL

        self.user32.ReleaseCapture.argtypes = []
        self.user32.ReleaseCapture.restype = wintypes.BOOL

        self.user32.SendMessageW.argtypes = [self.HWND, wintypes.UINT, self.WPARAM, self.LPARAM]
        self.user32.SendMessageW.restype = self.LRESULT

        self.user32.GetWindowRect.argtypes = [self.HWND, ctypes.POINTER(wintypes.RECT)]
        self.user32.GetWindowRect.restype = wintypes.BOOL

        self.user32.MonitorFromWindow.argtypes = [self.HWND, wintypes.DWORD]
        self.user32.MonitorFromWindow.restype = wintypes.HMONITOR

        class MONITORINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT),
                ("dwFlags", wintypes.DWORD),
            ]

        self.MONITORINFO = MONITORINFO
        self.user32.GetMonitorInfoW.argtypes = [wintypes.HMONITOR, ctypes.POINTER(MONITORINFO)]
        self.user32.GetMonitorInfoW.restype = wintypes.BOOL

        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        class MINMAXINFO(ctypes.Structure):
            _fields_ = [
                ("ptReserved", POINT),
                ("ptMaxSize", POINT),
                ("ptMaxPosition", POINT),
                ("ptMinTrackSize", POINT),
                ("ptMaxTrackSize", POINT),
            ]

        self.MINMAXINFO = MINMAXINFO

    # ------------------------------------------------------------------
    # Installation / fenêtre native
    # ------------------------------------------------------------------

    def _resolve_hwnd(self):
        if not self.available:
            return None
        try:
            self.root.update_idletasks()
            child = self.HWND(int(self.root.winfo_id()))
            # GA_ROOT = 2 : récupère le wrapper top-level créé par Tk.
            hwnd = self.user32.GetAncestor(child, 2)
            if not hwnd:
                hwnd = self.user32.GetParent(child) or child
            return hwnd
        except Exception:
            return None

    def install(self) -> bool:
        if not self.available:
            return False
        if self.installed:
            return True

        hwnd = self._resolve_hwnd()
        if not hwnd:
            return False

        self.hwnd = hwnd
        self._wndproc_callback = self.WNDPROC(self._wndproc)
        callback_ptr = self.ctypes.cast(self._wndproc_callback, self.ctypes.c_void_p).value
        if not callback_ptr:
            return False

        # GWLP_WNDPROC = -4
        old = self.user32.SetWindowLongPtrW(hwnd, -4, self.LONG_PTR(callback_ptr))
        if not old:
            return False
        self._old_wndproc = self.LONG_PTR(old)
        self.installed = True

        # Force immédiatement le recalcul de la zone non-client : le cadre
        # standard disparaît avant que l'utilisateur voie la fenêtre.
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

    def set_button_state_callback(self, callback: Callable[[bool], None] | None) -> None:
        self._button_state_callback = callback
        self._schedule_button_state_sync()

    def _schedule_button_state_sync(self) -> None:
        callback = self._button_state_callback
        if callback is None:
            return
        try:
            zoomed = self.is_maximized()
            self.root.after_idle(lambda: callback(zoomed))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Messages Windows
    # ------------------------------------------------------------------

    @staticmethod
    def _signed_word(value: int) -> int:
        value &= 0xFFFF
        return value - 0x10000 if value & 0x8000 else value

    def _resize_border(self) -> tuple[int, int]:
        # SM_CXSIZEFRAME / SM_CYSIZEFRAME + SM_CXPADDEDBORDER.
        try:
            frame_x = int(self.user32.GetSystemMetrics(32))
            frame_y = int(self.user32.GetSystemMetrics(33))
            padded = int(self.user32.GetSystemMetrics(92))
            return max(6, frame_x + padded), max(6, frame_y + padded)
        except Exception:
            return 8, 8

    def _hit_test_resize(self, lparam: int) -> int | None:
        if not self.hwnd or self.is_maximized():
            return None

        x = self._signed_word(int(lparam))
        y = self._signed_word(int(lparam) >> 16)
        rect = self.wintypes.RECT()
        if not self.user32.GetWindowRect(self.hwnd, self.ctypes.byref(rect)):
            return None

        bx, by = self._resize_border()
        left = x < rect.left + bx
        right = x >= rect.right - bx
        top = y < rect.top + by
        bottom = y >= rect.bottom - by

        # Valeurs HT* documentées par WM_NCHITTEST.
        if top and left:
            return 13  # HTTOPLEFT
        if top and right:
            return 14  # HTTOPRIGHT
        if bottom and left:
            return 16  # HTBOTTOMLEFT
        if bottom and right:
            return 17  # HTBOTTOMRIGHT
        if left:
            return 10  # HTLEFT
        if right:
            return 11  # HTRIGHT
        if top:
            return 12  # HTTOP
        if bottom:
            return 15  # HTBOTTOM
        return None

    def _apply_maximize_work_area(self, lparam: int) -> None:
        if not self.hwnd or not lparam:
            return
        MONITOR_DEFAULTTONEAREST = 2
        monitor = self.user32.MonitorFromWindow(self.hwnd, MONITOR_DEFAULTTONEAREST)
        if not monitor:
            return

        info = self.MONITORINFO()
        info.cbSize = self.ctypes.sizeof(self.MONITORINFO)
        if not self.user32.GetMonitorInfoW(monitor, self.ctypes.byref(info)):
            return

        mmi = self.ctypes.cast(lparam, self.ctypes.POINTER(self.MINMAXINFO)).contents
        monitor_rect = info.rcMonitor
        work = info.rcWork
        mmi.ptMaxPosition.x = work.left - monitor_rect.left
        mmi.ptMaxPosition.y = work.top - monitor_rect.top
        mmi.ptMaxSize.x = work.right - work.left
        mmi.ptMaxSize.y = work.bottom - work.top
        mmi.ptMaxTrackSize.x = mmi.ptMaxSize.x
        mmi.ptMaxTrackSize.y = mmi.ptMaxSize.y

    def _wndproc(self, hwnd, msg, wparam, lparam):
        try:
            WM_NCCALCSIZE = 0x0083
            WM_NCHITTEST = 0x0084
            WM_GETMINMAXINFO = 0x0024
            WM_SIZE = 0x0005

            if msg == WM_NCCALCSIZE and int(wparam):
                # Toute la fenêtre devient zone cliente : plus de barre de titre
                # ni de cadre standard, tout en conservant les styles natifs.
                return 0

            if msg == WM_NCHITTEST:
                hit = self._hit_test_resize(int(lparam))
                if hit is not None:
                    return hit

            if msg == WM_GETMINMAXINFO:
                self._apply_maximize_work_area(int(lparam))
                return 0

            if msg == WM_SIZE:
                self._schedule_button_state_sync()

        except Exception:
            # Un défaut du décor ne doit jamais casser la boucle de messages Tk.
            pass

        if self._old_wndproc:
            return self.user32.CallWindowProcW(
                self._old_wndproc,
                hwnd,
                msg,
                wparam,
                lparam,
            )
        return 0

    # ------------------------------------------------------------------
    # Commandes fenêtre
    # ------------------------------------------------------------------

    def prepare_restore_geometry(self, width_ratio: float = 0.84, height_ratio: float = 0.86) -> None:
        """Définit la taille normale que Windows retrouvera après restauration."""
        try:
            if not self.available or not self.hwnd:
                return
            monitor = self.user32.MonitorFromWindow(self.hwnd, 2)
            info = self.MONITORINFO()
            info.cbSize = self.ctypes.sizeof(self.MONITORINFO)
            if not monitor or not self.user32.GetMonitorInfoW(monitor, self.ctypes.byref(info)):
                return
            work = info.rcWork
            work_w = work.right - work.left
            work_h = work.bottom - work.top
            width = min(work_w, max(1180, int(work_w * width_ratio)))
            height = min(work_h, max(720, int(work_h * height_ratio)))
            x = work.left + max(0, (work_w - width) // 2)
            y = work.top + max(0, (work_h - height) // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            self.root.update_idletasks()
        except Exception:
            pass

    def minimize(self) -> None:
        if self.available and self.hwnd:
            self.user32.ShowWindow(self.hwnd, 6)  # SW_MINIMIZE
            return
        try:
            self.root.iconify()
        except Exception:
            pass

    def maximize(self) -> None:
        if self.available and self.hwnd:
            self.user32.ShowWindow(self.hwnd, 3)  # SW_MAXIMIZE
            self._schedule_button_state_sync()
            return
        try:
            self.root.state("zoomed")
        except Exception:
            pass

    def restore(self) -> None:
        if self.available and self.hwnd:
            self.user32.ShowWindow(self.hwnd, 9)  # SW_RESTORE
            self._schedule_button_state_sync()
            return
        try:
            self.root.state("normal")
        except Exception:
            pass

    def toggle_maximize(self) -> None:
        if self.is_maximized():
            self.restore()
        else:
            self.maximize()

    def is_maximized(self) -> bool:
        if self.available and self.hwnd:
            try:
                return bool(self.user32.IsZoomed(self.hwnd))
            except Exception:
                return False
        try:
            return str(self.root.state()) == "zoomed"
        except Exception:
            return False

    def close(self) -> None:
        if self.available and self.hwnd:
            self.user32.PostMessageW(self.hwnd, 0x0010, 0, 0)  # WM_CLOSE
            return
        try:
            self.root.destroy()
        except Exception:
            pass

    def begin_drag(self, _event=None) -> None:
        """Déplacement natif : même comportement qu'une vraie barre de titre."""
        if self.available and self.hwnd and not self.is_maximized():
            try:
                self.user32.ReleaseCapture()
                self.user32.SendMessageW(self.hwnd, 0x00A1, 2, 0)  # WM_NCLBUTTONDOWN / HTCAPTION
            except Exception:
                pass
