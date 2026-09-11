from __future__ import annotations

import multiprocessing as mp
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WAIT_MEDIA = (
    PROJECT_ROOT
    / "assets"
    / "branding"
    / "tomelinea"
    / "wait"
    / "TomeLinea_wait_model.gif"
)

WAIT_WIDTH = 640
WAIT_HEIGHT = 360
TARGET_CYCLE_MS = 3000
# Quand le travail est prêt, on termine proprement le mouvement en accélérant
# la fin du passage au lieu d'imposer les 3 secondes complètes.
FINISH_TAIL_MS = 360
FALLBACK_MIN_MS = 180


def _splash_worker(
    ready_event,
    started_event,
    media_path: str,
    width: int,
    height: int,
) -> None:
    try:
        import tkinter as tk
        from PIL import Image, ImageTk

        root = tk.Tk()
        root.withdraw()
        root.configure(bg="#061322")
        root.resizable(False, False)

        try:
            root.overrideredirect(True)
        except Exception:
            pass

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = max(0, (sw - width) // 2)
        y = max(0, (sh - height) // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

        label = tk.Label(
            root,
            bg="#061322",
            bd=0,
            highlightthickness=0,
        )
        label.place(x=0, y=0, width=width, height=height)

        try:
            root.attributes("-topmost", True)
        except Exception:
            pass

        animation = None
        frame_count = 0
        fallback_started = time.monotonic()

        try:
            animation = Image.open(media_path)
            frame_count = max(
                1,
                int(getattr(animation, "n_frames", 1)),
            )
        except Exception:
            animation = None
            frame_count = 0

        photos = []

        if animation is not None and frame_count > 0:
            try:
                for frame_index in range(frame_count):
                    animation.seek(frame_index)
                    frame = animation.convert("RGBA")

                    if frame.size != (width, height):
                        frame = frame.resize(
                            (width, height),
                            Image.LANCZOS,
                        )

                    photos.append(
                        ImageTk.PhotoImage(
                            frame,
                            master=root,
                        )
                    )

            except Exception:
                photos = []

        if photos:
            frame_count = len(photos)
            state = {
                "index": 0,
                "cycle_start": None,
                "finish_started": None,
                "finish_from_progress": None,
            }

            label.configure(
                image=photos[0],
                text="",
            )
            label.image = photos[0]

            root.deiconify()
            root.lift()
            root.update_idletasks()

            state["cycle_start"] = time.monotonic()
            started_event.set()

            cycle_seconds = TARGET_CYCLE_MS / 1000.0
            finish_seconds = max(0.08, FINISH_TAIL_MS / 1000.0)

            def advance() -> None:
                now = time.monotonic()
                cycle_start = state["cycle_start"]
                elapsed = now - cycle_start

                # Animation normale en boucle tant que le traitement travaille.
                completed_cycles = int(max(0.0, elapsed) // cycle_seconds)
                if completed_cycles:
                    cycle_start = cycle_start + completed_cycles * cycle_seconds
                    state["cycle_start"] = cycle_start
                    elapsed = now - cycle_start

                normal_progress = max(0.0, min(0.999999, elapsed / cycle_seconds))

                if ready_event.is_set():
                    # Le traitement vient de finir. On ne coupe pas le point
                    # lumineux au milieu : on accélère seulement le reste de son
                    # trajet jusqu'au dernier cadre. La fenêtre disparaît donc
                    # rapidement sans imposer une attente artificielle de 3 s.
                    if state["finish_started"] is None:
                        state["finish_started"] = now
                        state["finish_from_progress"] = normal_progress

                    start_progress = float(state["finish_from_progress"] or 0.0)
                    tail_elapsed = now - float(state["finish_started"] or now)
                    tail_ratio = max(0.0, min(1.0, tail_elapsed / finish_seconds))
                    progress = start_progress + (1.0 - start_progress) * tail_ratio

                    if tail_ratio >= 1.0:
                        photo = photos[-1]
                        label.configure(image=photo, text="")
                        label.image = photo
                        root.update_idletasks()
                        root.after(20, root.destroy)
                        return

                    delay_ms = 12
                else:
                    progress = normal_progress
                    index_preview = min(frame_count - 1, int(progress * frame_count))
                    next_frame_time = (
                        state["cycle_start"]
                        + ((index_preview + 1) / frame_count) * cycle_seconds
                    )
                    delay_ms = max(1, int(round((next_frame_time - time.monotonic()) * 1000)))

                index = min(frame_count - 1, int(progress * frame_count))

                if index != state["index"]:
                    state["index"] = index
                    photo = photos[index]
                    label.configure(
                        image=photo,
                        text="",
                    )
                    label.image = photo

                root.after(delay_ms, advance)

            root.after(1, advance)

        else:
            root.deiconify()
            root.lift()
            root.update_idletasks()
            fallback_started = time.monotonic()
            started_event.set()

            tk.Label(
                root,
                text="TOMELINEA",
                bg="#061322",
                fg="#F3F4F2",
                font=("Segoe UI", 18, "bold"),
            ).place(
                relx=0.5,
                rely=0.45,
                anchor="center",
            )

            def fallback_poll() -> None:
                elapsed_ms = int(
                    (time.monotonic() - fallback_started) * 1000
                )
                if (
                    ready_event.is_set()
                    and elapsed_ms >= FALLBACK_MIN_MS
                ):
                    root.destroy()
                    return
                root.after(20, fallback_poll)

            root.after(20, fallback_poll)

        root.mainloop()

    except Exception:
        try:
            started_event.set()
        except Exception:
            pass


@dataclass
class StartupAnimation:
    process: object | None
    ready_event: object | None
    started_event: object | None = None

    def wait_until_started(self, timeout: float = 0.8) -> bool:
        event = self.started_event
        if event is None:
            return False
        try:
            return bool(event.wait(timeout=max(0.0, float(timeout))))
        except Exception:
            return False

    def finish_after_cycle(
        self,
        *,
        pump: Callable[[], None] | None = None,
        timeout: float = 15.0,
    ) -> None:
        if self.ready_event is None:
            return

        try:
            self.ready_event.set()
        except Exception:
            return

        process = self.process
        if process is None:
            return

        deadline = time.monotonic() + timeout

        while True:
            try:
                alive = process.is_alive()
            except Exception:
                break

            if not alive:
                break

            if pump is not None:
                try:
                    pump()
                except Exception:
                    pass

            if time.monotonic() >= deadline:
                try:
                    process.terminate()
                except Exception:
                    pass
                break

            time.sleep(0.02)

        try:
            process.join(timeout=0.5)
        except Exception:
            pass


def start_startup_animation() -> StartupAnimation:
    try:
        ctx = mp.get_context("spawn")
        ready_event = ctx.Event()
        started_event = ctx.Event()

        process = ctx.Process(
            target=_splash_worker,
            args=(
                ready_event,
                started_event,
                str(WAIT_MEDIA),
                WAIT_WIDTH,
                WAIT_HEIGHT,
            ),
            daemon=True,
        )

        process.start()
        started_event.wait(timeout=2.5)

        return StartupAnimation(
            process=process,
            ready_event=ready_event,
            started_event=started_event,
        )

    except Exception:
        return StartupAnimation(
            process=None,
            ready_event=None,
            started_event=None,
        )

def start_wait_animation_async() -> StartupAnimation:
    """Même moteur d'attente que le lancement, sans attendre son affichage."""
    try:
        ctx = mp.get_context("spawn")
        ready_event = ctx.Event()
        started_event = ctx.Event()

        process = ctx.Process(
            target=_splash_worker,
            args=(
                ready_event,
                started_event,
                str(WAIT_MEDIA),
                WAIT_WIDTH,
                WAIT_HEIGHT,
            ),
            daemon=True,
        )

        process.start()

        return StartupAnimation(
            process=process,
            ready_event=ready_event,
            started_event=started_event,
        )

    except Exception:
        return StartupAnimation(
            process=None,
            ready_event=None,
            started_event=None,
        )

