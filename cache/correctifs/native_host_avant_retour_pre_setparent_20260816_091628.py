# -*- coding: utf-8 -*-
"""Hôte Win32 natif de TomeLinea V3.

Cette couche ne connaît ni A, ni B, ni C. Elle fournit uniquement la vraie
fenêtre Windows extérieure validée par le prototype indépendant, puis embarque
l'application Tkinter à l'intérieur.

Architecture adaptée du projet MIT :
https://github.com/grassator/win32-window-custom-titlebar

MIT License

Copyright (c) 2016 Domagoj "oberth" Pandža
Copyright (c) 2021 Dmitriy Kubyshkin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Type


# Couleurs TomeLinea. La fenêtre extérieure reste volontairement très sobre.
_WINDOW = (39, 45, 53)
_TITLE = (34, 40, 49)
_LINE = (89, 99, 109)
_TEXT = (243, 244, 242)
_BUTTON = (48, 54, 64)
_BUTTON_HOVER = (59, 89, 88)
_CLOSE_HOVER = (166, 67, 60)


def run_native_tomelinea(app_class: Type) -> None:
    """Lance TomeLinea dans une vraie fenêtre Win32 à barre personnalisée."""

    LRESULT = ctypes.c_ssize_t
    WPARAM = ctypes.c_size_t
    LPARAM = ctypes.c_ssize_t

    WNDPROC = ctypes.WINFUNCTYPE(
        LRESULT,
        wintypes.HWND,
        wintypes.UINT,
        WPARAM,
        LPARAM,
    )

    class WNDCLASSEXW(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.UINT),
            ("style", wintypes.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", wintypes.HICON),
            ("hCursor", wintypes.HANDLE),
            ("hbrBackground", wintypes.HBRUSH),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
            ("hIconSm", wintypes.HICON),
        ]

    class WINDOWPOS(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("hwndInsertAfter", wintypes.HWND),
            ("x", ctypes.c_int),
            ("y", ctypes.c_int),
            ("cx", ctypes.c_int),
            ("cy", ctypes.c_int),
            ("flags", wintypes.UINT),
        ]

    class NCCALCSIZE_PARAMS(ctypes.Structure):
        _fields_ = [
            ("rgrc", wintypes.RECT * 3),
            ("lppos", ctypes.POINTER(WINDOWPOS)),
        ]

    class PAINTSTRUCT(ctypes.Structure):
        _fields_ = [
            ("hdc", wintypes.HDC),
            ("fErase", wintypes.BOOL),
            ("rcPaint", wintypes.RECT),
            ("fRestore", wintypes.BOOL),
            ("fIncUpdate", wintypes.BOOL),
            ("rgbReserved", ctypes.c_byte * 32),
        ]

    class TRACKMOUSEEVENT(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("hwndTrack", wintypes.HWND),
            ("dwHoverTime", wintypes.DWORD),
        ]

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
    user32.DefWindowProcW.restype = LRESULT
    user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
    user32.RegisterClassExW.restype = wintypes.ATOM
    user32.CreateWindowExW.argtypes = [
        wintypes.DWORD,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.HWND,
        wintypes.HMENU,
        wintypes.HINSTANCE,
        wintypes.LPVOID,
    ]
    user32.CreateWindowExW.restype = wintypes.HWND
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindow.restype = wintypes.BOOL
    user32.UpdateWindow.argtypes = [wintypes.HWND]
    user32.UpdateWindow.restype = wintypes.BOOL
    user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetClientRect.restype = wintypes.BOOL
    user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    user32.GetCursorPos.restype = wintypes.BOOL
    user32.ScreenToClient.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    user32.ScreenToClient.restype = wintypes.BOOL
    user32.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    user32.SetWindowPos.restype = wintypes.BOOL
    user32.MoveWindow.argtypes = [
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.BOOL,
    ]
    user32.MoveWindow.restype = wintypes.BOOL
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
    user32.PostMessageW.restype = wintypes.BOOL
    user32.IsZoomed.argtypes = [wintypes.HWND]
    user32.IsZoomed.restype = wintypes.BOOL
    user32.InvalidateRect.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(wintypes.RECT),
        wintypes.BOOL,
    ]
    user32.InvalidateRect.restype = wintypes.BOOL
    user32.BeginPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]
    user32.BeginPaint.restype = wintypes.HDC
    user32.EndPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]
    user32.EndPaint.restype = wintypes.BOOL
    user32.FillRect.argtypes = [wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.HBRUSH]
    user32.FillRect.restype = ctypes.c_int
    user32.DrawTextW.argtypes = [
        wintypes.HDC,
        wintypes.LPCWSTR,
        ctypes.c_int,
        ctypes.POINTER(wintypes.RECT),
        wintypes.UINT,
    ]
    user32.DrawTextW.restype = ctypes.c_int
    user32.TrackMouseEvent.argtypes = [ctypes.POINTER(TRACKMOUSEEVENT)]
    user32.TrackMouseEvent.restype = wintypes.BOOL
    user32.LoadCursorW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR]
    user32.LoadCursorW.restype = wintypes.HANDLE
    user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    user32.GetSystemMetrics.restype = ctypes.c_int

    get_dpi_for_window = getattr(user32, "GetDpiForWindow", None)
    if get_dpi_for_window is not None:
        get_dpi_for_window.argtypes = [wintypes.HWND]
        get_dpi_for_window.restype = wintypes.UINT

    get_metric_for_dpi = getattr(user32, "GetSystemMetricsForDpi", None)
    if get_metric_for_dpi is not None:
        get_metric_for_dpi.argtypes = [ctypes.c_int, wintypes.UINT]
        get_metric_for_dpi.restype = ctypes.c_int

    set_dpi_context = getattr(user32, "SetProcessDpiAwarenessContext", None)
    if set_dpi_context is not None:
        set_dpi_context.argtypes = [ctypes.c_void_p]
        set_dpi_context.restype = wintypes.BOOL

    gdi32.CreateSolidBrush.argtypes = [wintypes.DWORD]
    gdi32.CreateSolidBrush.restype = wintypes.HBRUSH
    gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.SetBkMode.argtypes = [wintypes.HDC, ctypes.c_int]
    gdi32.SetBkMode.restype = ctypes.c_int
    gdi32.SetTextColor.argtypes = [wintypes.HDC, wintypes.DWORD]
    gdi32.SetTextColor.restype = wintypes.DWORD
    gdi32.GetStockObject.argtypes = [ctypes.c_int]
    gdi32.GetStockObject.restype = wintypes.HGDIOBJ
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi32.SelectObject.restype = wintypes.HGDIOBJ
    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HMODULE

    CS_VREDRAW = 0x0001
    CS_HREDRAW = 0x0002
    WS_THICKFRAME = 0x00040000
    WS_SYSMENU = 0x00080000
    WS_MAXIMIZEBOX = 0x00010000
    WS_MINIMIZEBOX = 0x00020000
    WS_CHILD = 0x40000000
    WS_VISIBLE = 0x10000000
    WS_CLIPCHILDREN = 0x02000000
    WS_EX_APPWINDOW = 0x00040000

    WM_CREATE = 0x0001
    WM_DESTROY = 0x0002
    WM_SIZE = 0x0005
    WM_PAINT = 0x000F
    WM_ERASEBKGND = 0x0014
    WM_NCCALCSIZE = 0x0083
    WM_NCHITTEST = 0x0084
    WM_CLOSE = 0x0010
    WM_MOUSEMOVE = 0x0200
    WM_LBUTTONUP = 0x0202
    WM_MOUSELEAVE = 0x02A3

    HTCLIENT = 1
    HTCAPTION = 2
    HTLEFT = 10
    HTRIGHT = 11
    HTTOP = 12
    HTTOPLEFT = 13
    HTTOPRIGHT = 14
    HTBOTTOM = 15
    HTBOTTOMLEFT = 16
    HTBOTTOMRIGHT = 17
    RESIZE_HITS = {
        HTLEFT,
        HTRIGHT,
        HTTOP,
        HTTOPLEFT,
        HTTOPRIGHT,
        HTBOTTOM,
        HTBOTTOMLEFT,
        HTBOTTOMRIGHT,
    }

    SW_NORMAL = 1
    SW_MINIMIZE = 6
    SW_MAXIMIZE = 3
    SW_SHOWMAXIMIZED = 3

    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOZORDER = 0x0004
    SWP_FRAMECHANGED = 0x0020

    SM_CXFRAME = 32
    SM_CYFRAME = 33
    SM_CXPADDEDBORDER = 92
    TME_LEAVE = 0x00000002
    HOVER_DEFAULT = 0xFFFFFFFF
    TRANSPARENT = 1
    DEFAULT_GUI_FONT = 17
    DT_LEFT = 0x00000000
    DT_CENTER = 0x00000001
    DT_VCENTER = 0x00000004
    DT_SINGLELINE = 0x00000020
    DT_END_ELLIPSIS = 0x00008000
    CW_USEDEFAULT = ctypes.c_int(0x80000000).value

    state = {
        "container": 0,
        "tk_hwnd": 0,
        "app": None,
        "original_destroy": None,
        "closing": False,
    }

    def rgb(r: int, g: int, b: int) -> int:
        return int(r) | (int(g) << 8) | (int(b) << 16)

    def dpi_for(hwnd) -> int:
        if get_dpi_for_window is not None:
            value = int(get_dpi_for_window(hwnd))
            if value:
                return value
        return 96

    def metric(index: int, dpi: int) -> int:
        if get_metric_for_dpi is not None:
            return int(get_metric_for_dpi(index, dpi))
        return int(round(user32.GetSystemMetrics(index) * dpi / 96.0))

    def scale(value: int, dpi: int) -> int:
        return max(1, int(round(value * dpi / 96.0)))

    def signed_word(value: int) -> int:
        return ctypes.c_short(value & 0xFFFF).value

    def point_from_lparam(value: int) -> tuple[int, int]:
        return signed_word(int(value)), signed_word(int(value) >> 16)

    def get_client_rect(hwnd) -> wintypes.RECT:
        rect = wintypes.RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rect))
        return rect

    def title_h(hwnd) -> int:
        return scale(46, dpi_for(hwnd))

    def button_w(hwnd) -> int:
        return scale(48, dpi_for(hwnd))

    def rect_contains(rect, x: int, y: int) -> bool:
        return rect.left <= x < rect.right and rect.top <= y < rect.bottom

    def button_rects(hwnd):
        rect = get_client_rect(hwnd)
        h = title_h(hwnd)
        w = button_w(hwnd)
        close_rect = wintypes.RECT(rect.right - w, 0, rect.right, h)
        max_rect = wintypes.RECT(rect.right - 2 * w, 0, rect.right - w, h)
        min_rect = wintypes.RECT(rect.right - 3 * w, 0, rect.right - 2 * w, h)
        return min_rect, max_rect, close_rect

    def button_at(hwnd, x: int, y: int):
        min_rect, max_rect, close_rect = button_rects(hwnd)
        if rect_contains(close_rect, x, y):
            return "close"
        if rect_contains(max_rect, x, y):
            return "max"
        if rect_contains(min_rect, x, y):
            return "min"
        return None

    def fill(hdc, rect, color) -> None:
        brush = gdi32.CreateSolidBrush(rgb(*color))
        try:
            user32.FillRect(hdc, ctypes.byref(rect), brush)
        finally:
            gdi32.DeleteObject(brush)

    def draw_text(hdc, text: str, rect, color, flags: int) -> None:
        gdi32.SetBkMode(hdc, TRANSPARENT)
        gdi32.SetTextColor(hdc, rgb(*color))
        font = gdi32.GetStockObject(DEFAULT_GUI_FONT)
        old = gdi32.SelectObject(hdc, font)
        try:
            user32.DrawTextW(hdc, text, -1, ctypes.byref(rect), flags)
        finally:
            gdi32.SelectObject(hdc, old)

    def pointer_in_client(hwnd):
        pt = wintypes.POINT()
        if not user32.GetCursorPos(ctypes.byref(pt)):
            return None
        if not user32.ScreenToClient(hwnd, ctypes.byref(pt)):
            return None
        return int(pt.x), int(pt.y)

    def resize_children(hwnd) -> None:
        container = int(state["container"] or 0)
        if not container:
            return

        rect = get_client_rect(hwnd)
        h = title_h(hwnd)
        width = max(1, int(rect.right - rect.left))
        height = max(1, int(rect.bottom - rect.top - h))

        user32.MoveWindow(wintypes.HWND(container), 0, h, width, height, True)

        tk_hwnd = int(state["tk_hwnd"] or 0)
        if tk_hwnd:
            try:
                user32.MoveWindow(wintypes.HWND(tk_hwnd), 0, 0, width, height, True)
            except Exception:
                pass

    @WNDPROC
    def wndproc(hwnd, message, w_param, l_param):
        if message == WM_NCCALCSIZE:
            if not w_param:
                return user32.DefWindowProcW(hwnd, message, w_param, l_param)

            dpi = dpi_for(hwnd)
            frame_x = metric(SM_CXFRAME, dpi)
            frame_y = metric(SM_CYFRAME, dpi)
            padding = metric(SM_CXPADDEDBORDER, dpi)

            params = ctypes.cast(l_param, ctypes.POINTER(NCCALCSIZE_PARAMS)).contents
            requested = params.rgrc[0]
            requested.left += frame_x + padding
            requested.right -= frame_x + padding
            requested.bottom -= frame_y + padding
            if user32.IsZoomed(hwnd):
                requested.top += frame_y + padding
            params.rgrc[0] = requested
            return 0

        if message == WM_CREATE:
            user32.SetWindowPos(
                hwnd,
                None,
                0,
                0,
                0,
                0,
                SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER,
            )
            return 0

        if message == WM_NCHITTEST:
            hit = int(user32.DefWindowProcW(hwnd, message, w_param, l_param))
            if hit in RESIZE_HITS:
                return hit

            sx, sy = point_from_lparam(l_param)
            pt = wintypes.POINT(sx, sy)
            user32.ScreenToClient(hwnd, ctypes.byref(pt))

            if button_at(hwnd, int(pt.x), int(pt.y)) is not None:
                return HTCLIENT

            dpi = dpi_for(hwnd)
            frame_y = metric(SM_CYFRAME, dpi)
            padding = metric(SM_CXPADDEDBORDER, dpi)
            if not user32.IsZoomed(hwnd) and 0 < pt.y < frame_y + padding:
                return HTTOP
            if pt.y < title_h(hwnd):
                return HTCAPTION
            return HTCLIENT

        if message == WM_SIZE:
            resize_children(hwnd)
            user32.InvalidateRect(hwnd, None, False)
            return user32.DefWindowProcW(hwnd, message, w_param, l_param)

        if message == WM_MOUSEMOVE:
            tme = TRACKMOUSEEVENT(
                ctypes.sizeof(TRACKMOUSEEVENT),
                TME_LEAVE,
                hwnd,
                HOVER_DEFAULT,
            )
            user32.TrackMouseEvent(ctypes.byref(tme))
            top = wintypes.RECT(0, 0, get_client_rect(hwnd).right, title_h(hwnd))
            user32.InvalidateRect(hwnd, ctypes.byref(top), False)
            return 0

        if message == WM_MOUSELEAVE:
            top = wintypes.RECT(0, 0, get_client_rect(hwnd).right, title_h(hwnd))
            user32.InvalidateRect(hwnd, ctypes.byref(top), False)
            return 0

        if message == WM_LBUTTONUP:
            x, y = point_from_lparam(l_param)
            which = button_at(hwnd, x, y)
            if which == "close":
                user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                return 0
            if which == "min":
                user32.ShowWindow(hwnd, SW_MINIMIZE)
                return 0
            if which == "max":
                user32.ShowWindow(hwnd, SW_NORMAL if user32.IsZoomed(hwnd) else SW_MAXIMIZE)
                return 0

        if message == WM_ERASEBKGND:
            return 1

        if message == WM_PAINT:
            ps = PAINTSTRUCT()
            hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
            try:
                rect = get_client_rect(hwnd)
                fill(hdc, rect, _WINDOW)
                h = title_h(hwnd)
                title_rect = wintypes.RECT(0, 0, rect.right, h)
                fill(hdc, title_rect, _TITLE)
                line = wintypes.RECT(0, h - 1, rect.right, h)
                fill(hdc, line, _LINE)

                min_rect, max_rect, close_rect = button_rects(hwnd)
                hover = None
                pos = pointer_in_client(hwnd)
                if pos:
                    hover = button_at(hwnd, pos[0], pos[1])

                for name, button_rect in (
                    ("min", min_rect),
                    ("max", max_rect),
                    ("close", close_rect),
                ):
                    color = _BUTTON
                    if hover == name:
                        color = _CLOSE_HOVER if name == "close" else _BUTTON_HOVER
                    fill(hdc, button_rect, color)

                title_text = wintypes.RECT(
                    scale(18, dpi_for(hwnd)),
                    0,
                    min_rect.left - scale(10, dpi_for(hwnd)),
                    h,
                )
                draw_text(
                    hdc,
                    "TomeLinea",
                    title_text,
                    _TEXT,
                    DT_LEFT | DT_VCENTER | DT_SINGLELINE | DT_END_ELLIPSIS,
                )
                draw_text(hdc, "—", min_rect, _TEXT, DT_CENTER | DT_VCENTER | DT_SINGLELINE)
                draw_text(
                    hdc,
                    "❐" if user32.IsZoomed(hwnd) else "□",
                    max_rect,
                    _TEXT,
                    DT_CENTER | DT_VCENTER | DT_SINGLELINE,
                )
                draw_text(hdc, "✕", close_rect, _TEXT, DT_CENTER | DT_VCENTER | DT_SINGLELINE)
            finally:
                user32.EndPaint(hwnd, ctypes.byref(ps))
            return 0

        if message == WM_CLOSE:
            state["closing"] = True
            return user32.DefWindowProcW(hwnd, message, w_param, l_param)

        if message == WM_DESTROY:
            app = state.get("app")
            if app is not None:
                try:
                    app.after_idle(app.quit)
                except Exception:
                    try:
                        app.quit()
                    except Exception:
                        pass
            return 0

        return user32.DefWindowProcW(hwnd, message, w_param, l_param)

    if set_dpi_context is not None:
        try:
            set_dpi_context(ctypes.c_void_p(-4))
        except Exception:
            pass

    hinstance = kernel32.GetModuleHandleW(None)
    class_name = "TOMELINEA_V3_NATIVE_HOST_V1"

    cursor_id = ctypes.cast(ctypes.c_void_p(32512), wintypes.LPCWSTR)
    wc = WNDCLASSEXW()
    wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
    wc.style = CS_HREDRAW | CS_VREDRAW
    wc.lpfnWndProc = wndproc
    wc.cbClsExtra = 0
    wc.cbWndExtra = 0
    wc.hInstance = hinstance
    wc.hIcon = None
    wc.hCursor = user32.LoadCursorW(None, cursor_id)
    wc.hbrBackground = None
    wc.lpszMenuName = None
    wc.lpszClassName = class_name
    wc.hIconSm = None

    atom = user32.RegisterClassExW(ctypes.byref(wc))
    if not atom:
        error = ctypes.get_last_error()
        if error != 1410:
            raise ctypes.WinError(error)

    style = WS_THICKFRAME | WS_SYSMENU | WS_MAXIMIZEBOX | WS_MINIMIZEBOX | WS_CLIPCHILDREN
    hwnd = user32.CreateWindowExW(
        WS_EX_APPWINDOW,
        class_name,
        "TomeLinea",
        style,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        1280,
        820,
        None,
        None,
        hinstance,
        None,
    )
    if not hwnd:
        raise ctypes.WinError(ctypes.get_last_error())

    rect = get_client_rect(hwnd)
    h = title_h(hwnd)
    container = user32.CreateWindowExW(
        0,
        "STATIC",
        "",
        WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN,
        0,
        h,
        max(1, rect.right),
        max(1, rect.bottom - h),
        hwnd,
        None,
        hinstance,
        None,
    )
    if not container:
        raise ctypes.WinError(ctypes.get_last_error())
    state["container"] = int(container)

    app = app_class(use=f"0x{int(container):x}", native_embedded=True)
    state["app"] = app
    app.update_idletasks()
    try:
        state["tk_hwnd"] = int(app.winfo_id())
    except Exception:
        state["tk_hwnd"] = 0

    # Toutes les fermetures déjà existantes dans TomeLinea ferment désormais
    # l'hôte Win32 extérieur au lieu de détruire seulement le contenu Tk.
    original_destroy = app.destroy
    state["original_destroy"] = original_destroy

    def request_native_close() -> None:
        if not state["closing"]:
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

    app.destroy = request_native_close

    resize_children(hwnd)
    user32.ShowWindow(hwnd, SW_SHOWMAXIMIZED)
    user32.UpdateWindow(hwnd)

    try:
        app.mainloop()
    finally:
        try:
            app.destroy = original_destroy
        except Exception:
            pass
        try:
            original_destroy()
        except Exception:
            pass
