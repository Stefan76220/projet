from __future__ import annotations

import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = PROJECT_ROOT / "runtime"
RUNTIME_PY = RUNTIME_ROOT / "python"
WEB_ROOT = PROJECT_ROOT / "src" / "gui_v3" / "viewer3d" / "web"
THREE_ROOT = WEB_ROOT / "vendor" / "three"
CACHE_ROOT = PROJECT_ROOT / "cache"
STATE_FILE = CACHE_ROOT / "viewer_runtime_state.json"
LOG_FILE = CACHE_ROOT / "viewer_runtime_prepare.log"

TKWRY_VERSION = "0.1.4"
WEBVIEW2_BOOTSTRAPPER = "https://go.microsoft.com/fwlink/p/?LinkId=2124703"
THREE_FILES: dict[str, tuple[str, int]] = {
    "three.module.js": (
        "https://cdn.jsdelivr.net/npm/three@0.185.1/build/three.module.js",
        1_000,
    ),
    "three.core.js": (
        "https://cdn.jsdelivr.net/npm/three@0.185.1/build/three.core.js",
        100_000,
    ),
    "addons/environments/RoomEnvironment.js": (
        "https://cdn.jsdelivr.net/npm/three@0.185.1/examples/jsm/environments/RoomEnvironment.js",
        1_000,
    ),
}


def _creation_flags() -> int:
    if os.name == "nt":
        return int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return 0


def _log(text: str) -> None:
    try:
        CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(f"[{stamp}] {text}\n")
    except Exception:
        pass


def activate_local_runtime() -> None:
    """Rend les composants Python préparés par TomeLinea importables."""
    if RUNTIME_PY.is_dir():
        value = str(RUNTIME_PY)
        if value not in sys.path:
            sys.path.insert(0, value)


def _tkwry_ready() -> bool:
    activate_local_runtime()
    try:
        return importlib.util.find_spec("tkwry") is not None
    except Exception:
        return False


def _install_tkwry() -> None:
    RUNTIME_PY.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-input",
        "--only-binary=:all:",
        "--upgrade",
        "--target",
        str(RUNTIME_PY),
        f"tkwry=={TKWRY_VERSION}",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=_creation_flags(),
        timeout=180,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()[-2500:]
        raise RuntimeError(f"Installation du moteur interne impossible.\n{detail}")
    activate_local_runtime()
    if not _tkwry_ready():
        raise RuntimeError("Le moteur interne a été installé mais reste introuvable.")


def _valid_file(path: Path, minimum_size: int) -> bool:
    try:
        return path.is_file() and path.stat().st_size >= minimum_size
    except Exception:
        return False


def three_assets_ready() -> bool:
    return all(
        _valid_file(THREE_ROOT / relative, minimum)
        for relative, (_url, minimum) in THREE_FILES.items()
    )


def _download(url: str, target: Path, *, timeout: int = 60) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "TomeLinea/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read()
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_bytes(data)
    temp.replace(target)


def _prepare_three_assets() -> None:
    for relative, (url, minimum) in THREE_FILES.items():
        target = THREE_ROOT / relative
        if _valid_file(target, minimum):
            continue
        _download(url, target)
        if not _valid_file(target, minimum):
            raise RuntimeError(f"Fichier 3D incomplet : {relative}")


def _webview2_candidates() -> list[Path]:
    roots: list[Path] = []
    for env_name in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"):
        raw = os.environ.get(env_name)
        if raw:
            roots.append(Path(raw))
    candidates: list[Path] = []
    for root in roots:
        base = root / "Microsoft" / "EdgeWebView" / "Application"
        if not base.is_dir():
            continue
        try:
            candidates.extend(base.glob("*/msedgewebview2.exe"))
        except Exception:
            pass
    return candidates


def webview2_ready() -> bool:
    if os.name != "nt":
        return True
    return any(path.is_file() for path in _webview2_candidates())


def _install_webview2() -> None:
    if os.name != "nt" or webview2_ready():
        return
    installer_dir = RUNTIME_ROOT / "installers"
    installer_dir.mkdir(parents=True, exist_ok=True)
    installer = installer_dir / "MicrosoftEdgeWebView2Setup.exe"
    _download(WEBVIEW2_BOOTSTRAPPER, installer, timeout=90)
    result = subprocess.run(
        [str(installer), "/silent", "/install"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=_creation_flags(),
        timeout=240,
    )
    if result.returncode not in (0, 3010):
        detail = (result.stderr or result.stdout or "").strip()[-2000:]
        raise RuntimeError(f"Installation WebView2 impossible (code {result.returncode}).\n{detail}")
    # Quelques installations mettent un court instant à publier le runtime.
    for _ in range(20):
        if webview2_ready():
            break
        time.sleep(0.25)


def runtime_status() -> dict[str, object]:
    return {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "tkwry": _tkwry_ready(),
        "three": three_assets_ready(),
        "webview2": webview2_ready(),
    }


class _Splash:
    def __init__(self) -> None:
        self.root = None
        self.status = None
        self.detail = None
        try:
            import tkinter as tk
            from tkinter import ttk

            root = tk.Tk()
            root.withdraw()
            root.title("TomeLinea — Préparation")
            root.configure(bg="#222831")
            try:
                root.overrideredirect(True)
            except Exception:
                pass

            width, height = 560, 220
            sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
            x = max(0, (sw - width) // 2)
            y = max(0, (sh - height) // 2)
            root.geometry(f"{width}x{height}+{x}+{y}")

            frame = tk.Frame(root, bg="#222831", highlightbackground="#59636D", highlightthickness=1)
            frame.pack(fill="both", expand=True)
            tk.Label(
                frame,
                text="TOMELINEA",
                bg="#222831",
                fg="#F3F4F2",
                font=("Segoe UI", 18, "bold"),
            ).pack(pady=(30, 3))
            tk.Label(
                frame,
                text="Préparation du moteur de visualisation",
                bg="#222831",
                fg="#9FD0C4",
                font=("Segoe UI", 10, "bold"),
            ).pack()

            self.status = tk.StringVar(value="Vérification des composants…")
            self.detail = tk.StringVar(value="")
            tk.Label(
                frame,
                textvariable=self.status,
                bg="#222831",
                fg="#F3F4F2",
                font=("Segoe UI", 10),
            ).pack(pady=(26, 5))
            tk.Label(
                frame,
                textvariable=self.detail,
                bg="#222831",
                fg="#89939B",
                font=("Segoe UI", 8),
            ).pack()
            bar = ttk.Progressbar(frame, mode="indeterminate", length=410)
            bar.pack(pady=(14, 0))
            bar.start(12)

            self.root = root
            root.deiconify()
            root.lift()
            root.update_idletasks()
            root.update()
        except Exception:
            self.root = None

    def update(self, status: str, detail: str = "") -> None:
        if self.root is None:
            return
        try:
            self.status.set(status)
            self.detail.set(detail)
            self.root.update_idletasks()
            self.root.update()
        except Exception:
            pass

    def close(self) -> None:
        if self.root is None:
            return
        try:
            self.root.destroy()
        except Exception:
            pass
        self.root = None



class LaunchPreparation:
    """Fenêtre de préparation gardée ouverte pendant le préchauffage réel."""

    def __init__(self, splash: _Splash, status: dict[str, object]) -> None:
        self._splash = splash
        self.status = status

    def update(self, status: str, detail: str = "") -> None:
        self._splash.update(status, detail)

    def close(self) -> None:
        self._splash.close()


def prepare_before_launch(*, keep_window: bool = False) -> dict[str, object] | LaunchPreparation:
    """Prépare les moteurs du Visionneur avant le lancement normal de TomeLinea.

    La préparation est idempotente : après le premier passage, les lancements
    suivants ne font que des contrôles locaux très rapides.
    """
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    splash = _Splash()
    errors: list[str] = []
    keep_alive = False

    try:
        splash.update("Moteur d’intégration", "Vérification du composant interne…")
        if os.name == "nt" and not _tkwry_ready():
            try:
                _install_tkwry()
            except Exception as exc:
                errors.append(str(exc))
                _log(f"tkwry: {type(exc).__name__}: {exc}")

        splash.update("Moteur 3D", "Préparation des ressources locales Three.js…")
        if not three_assets_ready():
            try:
                _prepare_three_assets()
            except Exception as exc:
                errors.append(str(exc))
                _log(f"three: {type(exc).__name__}: {exc}")

        splash.update("Moteur Windows", "Vérification de Microsoft WebView2…")
        if os.name == "nt" and not webview2_ready():
            try:
                _install_webview2()
            except Exception as exc:
                errors.append(str(exc))
                _log(f"webview2: {type(exc).__name__}: {exc}")

        status = runtime_status()
        status["errors"] = errors
        status["viewer_ready"] = bool(
            (status.get("tkwry") or os.name != "nt")
            and status.get("three")
            and status.get("webview2")
        )
        try:
            STATE_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

        if status["viewer_ready"]:
            splash.update("Moteur prêt", "Préchargement du Visionneur…")
        else:
            splash.update("TomeLinea va s’ouvrir", "Le Visionneur sera reproposé au prochain lancement.")

        if keep_window:
            keep_alive = True
            return LaunchPreparation(splash, status)
        return status
    finally:
        if not keep_alive:
            splash.close()
