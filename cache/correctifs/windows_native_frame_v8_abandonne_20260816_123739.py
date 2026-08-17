from __future__ import annotations

"""Cadre Windows natif pour TomeLinea V3.

Le point essentiel est qu'il n'existe qu'un seul HWND : celui du toplevel Tk.
Windows reste responsable de la maximisation/restauration et Tk reçoit donc
les messages de taille sur sa propre fenêtre, sans coque Win32 intermédiaire.

La gestion de WM_NCCALCSIZE suit le principe du projet de référence
``grassator/win32-window-custom-titlebar`` : les styles natifs de fenêtre sont
conservés (redimensionnement, Snap, barre des tâches, Alt+Tab), tandis que la
zone cliente est étendue dans l'ancienne barre de titre.
"""

import sys
from typing import Callable


class WindowsNativeFrame:
    """Habillage natif Win32 appliqué directement à la fenêtre Tk."""

    def __init__(self, root, *, caption_height: int = 34) -> None:
        self.root = root
        self.available = sys.platform == "win32"
        self.caption_height = max(24, int(caption_height))
        self.installed = False
        self.hwnd = None
        self._old_wndproc = None
        self._wndproc_callback = None
        self._state_callback: Callable[[bool], None] | None = None
        self._transition_in_progress = False

        if self.available:
            self._init_win32()

    # ------------------------------------------------------------------
    # Initialisation Win32
    # ------------------------------------------------------------------

    def _init_win32(self) -> None:
        import ctypes
        from ctypes import wintypes

        self.ctypes = ctypes
        self.wintypes = wintypes
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)

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

        class NCCALCSIZE_PARAMS(ctypes.Structure):
            _fields_ = [
                ("rgrc", wintypes.RECT * 3),
                ("lppos", ctypes.c_void_p),
            ]

        self.NCCALCSIZE_PARAMS = NCCALCSIZE_PARAMS

        self.user32.GetAncestor.argtypes = [self.HWND, wintypes.UINT]
        self.user32.GetAncestor.restype = self.HWND
        self.user32.GetParent.argtypes = [self.HWND]
        self.user32.GetParent.restype = self.HWND

        self.user32.GetWindowLongPtrW.argtypes = [self.HWND, ctypes.c_int]
        self.user32.GetWindowLongPtrW.restype = self.LONG_PTR
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
        self.user32.DefWindowProcW.argtypes = [
            self.HWND,
            self.UINT,
            self.WPARAM,
            self.LPARAM,
        ]
        self.user32.DefWindowProcW.restype = self.LRESULT

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
        self.user32.SendMessageW.argtypes = [
            self.HWND,
            wintypes.UINT,
            self.WPARAM,
            self.LPARAM,
        ]
        self.user32.SendMessageW.restype = self.LRESULT
        self.user32.RedrawWindow.argtypes = [
            self.HWND,
            ctypes.c_void_p,
            wintypes.HRGN,
            wintypes.UINT,
        ]
        self.user32.RedrawWindow.restype = wintypes.BOOL
        self.user32.GetSystemMetrics.argtypes = [ctypes.c_int]
        self.user32.GetSystemMetrics.restype = ctypes.c_int

        self.get_dpi_for_window = getattr(self.user32, "GetDpiForWindow", None)
        if self.get_dpi_for_window is not None:
            self.get_dpi_for_window.argtypes = [self.HWND]
            self.get_dpi_for_window.restype = wintypes.UINT

        self.get_system_metrics_for_dpi = getattr(
            self.user32, "GetSystemMetricsForDpi", None
        )
        if self.get_system_metrics_for_dpi is not None:
            self.get_system_metrics_for_dpi.argtypes = [ctypes.c_int, wintypes.UINT]
            self.get_system_metrics_for_dpi.restype = ctypes.c_int

    def _resolve_hwnd(self):
        if not self.available:
            return None
        try:
            self.root.update_idletasks()
            tk_child = self.HWND(int(self.root.winfo_id()))
            # Tk crée un wrapper Win32 autour de la fenêtre widget elle-même.
            # C'est ce wrapper top-level qu'il faut sous-classer.
            hwnd = self.user32.GetAncestor(tk_child, 2)  # GA_ROOT
            if not hwnd:
                hwnd = self.user32.GetParent(tk_child) or tk_child
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

        # On conserve explicitement les capacités d'une vraie fenêtre Windows.
        GWL_STYLE = -16
        WS_CAPTION = 0x00C00000
        WS_THICKFRAME = 0x00040000
        WS_SYSMENU = 0x00080000
        WS_MINIMIZEBOX = 0x00020000
        WS_MAXIMIZEBOX = 0x00010000
        WS_CLIPCHILDREN = 0x02000000

        style = int(self.user32.GetWindowLongPtrW(hwnd, GWL_STYLE))
        style |= (
            WS_CAPTION
            | WS_THICKFRAME
            | WS_SYSMENU
            | WS_MINIMIZEBOX
            | WS_MAXIMIZEBOX
            | WS_CLIPCHILDREN
        )
        self.user32.SetWindowLongPtrW(hwnd, GWL_STYLE, self.LONG_PTR(style))

        self._wndproc_callback = self.WNDPROC(self._wndproc)
        callback_ptr = self.ctypes.cast(
            self._wndproc_callback, self.ctypes.c_void_p
        ).value
        if not callback_ptr:
            return False

        GWLP_WNDPROC = -4
        old = self.user32.SetWindowLongPtrW(
            hwnd, GWLP_WNDPROC, self.LONG_PTR(callback_ptr)
        )
        if not old:
            return False
        self._old_wndproc = self.LONG_PTR(old)
        self.installed = True

        # Demande à Windows de recalculer immédiatement le non-client avec
        # notre WM_NCCALCSIZE, avant que la fenêtre ne soit révélée.
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
            SWP_NOSIZE
            | SWP_NOMOVE
            | SWP_NOZORDER
            | SWP_NOACTIVATE
            | SWP_FRAMECHANGED,
        )
        return True

    # ------------------------------------------------------------------
    # Géométrie non-client / hit testing
    # ------------------------------------------------------------------

    def _dpi(self, hwnd) -> int:
        try:
            if self.get_dpi_for_window is not None:
                dpi = int(self.get_dpi_for_window(hwnd))
                if dpi:
                    return dpi
        except Exception:
            pass
        return 96

    def _metric(self, index: int, dpi: int) -> int:
        try:
            if self.get_system_metrics_for_dpi is not None:
                return int(self.get_system_metrics_for_dpi(index, dpi))
        except Exception:
            pass
        return int(round(self.user32.GetSystemMetrics(index) * dpi / 96.0))

    @staticmethod
    def _signed_word(value: int) -> int:
        value &= 0xFFFF
        return value - 0x10000 if value & 0x8000 else value

    def _caption_pixels(self, hwnd) -> int:
        return max(24, int(round(self.caption_height * self._dpi(hwnd) / 96.0)))

    def _handle_nccalcsize(self, hwnd, wparam, lparam) -> int | None:
        if not int(wparam):
            return None

        # Même principe que le code Win32 de référence : le cadre redimensionnable
        # reste pris en compte sur les côtés et en bas. Seule l'ancienne barre de
        # titre est transformée en zone cliente. En maximisé, l'inset supérieur
        # évite le débordement invisible que Windows ajoute autour d'une fenêtre
        # maximisée.
        dpi = self._dpi(hwnd)
        frame_x = self._metric(32, dpi)  # SM_CXFRAME
        frame_y = self._metric(33, dpi)  # SM_CYFRAME
        padding = self._metric(92, dpi)  # SM_CXPADDEDBORDER

        params = self.ctypes.cast(
            lparam, self.ctypes.POINTER(self.NCCALCSIZE_PARAMS)
        ).contents
        requested = params.rgrc[0]
        requested.left += frame_x + padding
        requested.right -= frame_x + padding
        requested.bottom -= frame_y + padding
        if self.user32.IsZoomed(hwnd):
            requested.top += frame_y + padding
        params.rgrc[0] = requested
        return 0

    def _handle_nchittest(self, hwnd, msg, wparam, lparam) -> int:
        # Le DefWindowProc garde la logique native des bordures/corners : resize,
        # Aero Snap et curseurs restent ceux de Windows.
        hit = int(self.user32.DefWindowProcW(hwnd, msg, wparam, lparam))
        resize_hits = {10, 11, 12, 13, 14, 15, 16, 17}
        if hit in resize_hits:
            return hit

        x = self._signed_word(int(lparam))
        y = self._signed_word(int(lparam) >> 16)

        pt = self.wintypes.POINT(x, y)
        try:
            self.user32.ScreenToClient.argtypes = [
                self.HWND,
                self.ctypes.POINTER(self.wintypes.POINT),
            ]
            self.user32.ScreenToClient.restype = self.wintypes.BOOL
            self.user32.ScreenToClient(hwnd, self.ctypes.byref(pt))
        except Exception:
            return 1  # HTCLIENT

        # Bande très supérieure volontairement vide dans TomeLinea : elle sert
        # de vraie zone de déplacement Windows sans ajouter une deuxième barre.
        if 0 <= int(pt.y) < self._caption_pixels(hwnd):
            return 2  # HTCAPTION
        return 1  # HTCLIENT

    # ------------------------------------------------------------------
    # Synchronisation d'état
    # ------------------------------------------------------------------

    def set_state_callback(self, callback: Callable[[bool], None] | None) -> None:
        self._state_callback = callback
        self._schedule_state_sync()

    def _schedule_state_sync(self) -> None:
        callback = self._state_callback
        if callback is None:
            return
        try:
            zoomed = self.is_maximized()
            self.root.after_idle(lambda z=zoomed: callback(z))
        except Exception:
            pass

    def _wndproc(self, hwnd, msg, wparam, lparam):
        try:
            WM_NCCALCSIZE = 0x0083
            WM_NCHITTEST = 0x0084
            WM_SIZE = 0x0005
            WM_NCLBUTTONDBLCLK = 0x00A3
            WM_SYSCOMMAND = 0x0112
            HTCAPTION = 2
            SC_MAXIMIZE = 0xF030
            SC_RESTORE = 0xF120

            if msg == WM_NCCALCSIZE:
                result = self._handle_nccalcsize(hwnd, wparam, lparam)
                if result is not None:
                    return result

            if msg == WM_NCHITTEST:
                return self._handle_nchittest(hwnd, msg, wparam, lparam)

            if msg == WM_NCLBUTTONDBLCLK and int(wparam) == HTCAPTION:
                # Le double-clic utilise la même transition atomique que le
                # bouton TomeLinea au lieu de laisser deux HWND se désynchroniser.
                self.root.after_idle(self.toggle_maximize)
                return 0

            if msg == WM_SYSCOMMAND and not self._transition_in_progress:
                command = int(wparam) & 0xFFF0
                if command == SC_MAXIMIZE:
                    self.root.after_idle(self.maximize)
                    return 0
                if command == SC_RESTORE:
                    self.root.after_idle(self.restore)
                    return 0

            if msg == WM_SIZE:
                self._schedule_state_sync()

        except Exception:
            # Le décor ne doit jamais casser la boucle de messages Tk.
            pass

        if self._old_wndproc:
            return self.user32.CallWindowProcW(
                self._old_wndproc, hwnd, msg, wparam, lparam
            )
        return self.user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    # ------------------------------------------------------------------
    # Commandes de fenêtre
    # ------------------------------------------------------------------

    def prepare_restore_geometry(
        self, width_ratio: float = 0.84, height_ratio: float = 0.86
    ) -> None:
        """Prépare la géométrie normale que Windows retrouvera au restore."""
        if not self.available:
            return
        try:
            screen_w = int(self.root.winfo_screenwidth())
            screen_h = int(self.root.winfo_screenheight())
            width = max(1180, int(screen_w * width_ratio))
            height = max(720, int(screen_h * height_ratio))
            width = min(screen_w, width)
            height = min(screen_h, height)
            x = max(0, (screen_w - width) // 2)
            y = max(0, (screen_h - height) // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            self.root.update_idletasks()
        except Exception:
            pass

    def _atomic_show(self, command: int) -> None:
        """Change d'état sans afficher un client Tk à moitié recalculé.

        Windows redimensionne le vrai HWND de Tk. Le redraw est suspendu le
        temps que Tk traite la nouvelle géométrie, puis toute la hiérarchie est
        repeinte en une seule passe. Cela supprime la phase « coque agrandie /
        ancien contenu dans le coin » observée dans la vidéo de test.
        """
        if not (self.available and self.hwnd):
            return
        if self._transition_in_progress:
            return

        WM_SETREDRAW = 0x000B
        RDW_INVALIDATE = 0x0001
        RDW_ERASE = 0x0004
        RDW_ALLCHILDREN = 0x0080
        RDW_UPDATENOW = 0x0100
        RDW_FRAME = 0x0400

        self._transition_in_progress = True
        redraw_disabled = False
        try:
            self.user32.SendMessageW(self.hwnd, WM_SETREDRAW, 0, 0)
            redraw_disabled = True

            self.user32.ShowWindow(self.hwnd, command)

            # ShowWindow a déjà envoyé WM_SIZE. update() vide alors la file Tk,
            # y compris les Configure/layout, pendant que rien n'est peint.
            self.root.update_idletasks()
            self.root.update()

        finally:
            if redraw_disabled:
                try:
                    self.user32.SendMessageW(self.hwnd, WM_SETREDRAW, 1, 0)
                    self.user32.RedrawWindow(
                        self.hwnd,
                        None,
                        None,
                        RDW_INVALIDATE
                        | RDW_ERASE
                        | RDW_FRAME
                        | RDW_ALLCHILDREN
                        | RDW_UPDATENOW,
                    )
                except Exception:
                    pass
            self._transition_in_progress = False
            self._schedule_state_sync()

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
            self._atomic_show(3)  # SW_MAXIMIZE
            return
        try:
            self.root.state("zoomed")
        except Exception:
            pass

    def restore(self) -> None:
        if self.available and self.hwnd:
            self._atomic_show(9)  # SW_RESTORE
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
