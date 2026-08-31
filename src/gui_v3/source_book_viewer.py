from __future__ import annotations

"""TomeLinea — composant intégré de consultation de la Source du livre.

Le widget est importé et hébergé par TomeLinea (Structure puis Gabarits).
Il n'est pas un programme autonome et ne modifie jamais le document auteur.
"""

from pathlib import Path
import tkinter as tk

from PIL import Image, ImageTk

from src.core.book_source import inspect_pdf, render_pdf_page


class SourceBookViewer(tk.Frame):
    def __init__(
        self,
        parent,
        source: str | Path,
        *,
        cache_dir: str | Path | None = None,
        initial_page: int = 1,
        bg: str = "#1C222A",
        panel_bg: str = "#252C35",
        fg: str = "#E7E9EC",
        muted: str = "#AEB5BD",
        accent: str = "#C6A96B",
        on_page_changed=None,
        page_trace_provider=None,
    ) -> None:
        super().__init__(parent, bg=bg, takefocus=True)

        self.source = Path(source).expanduser().resolve()
        self.info = inspect_pdf(self.source)
        self.page_count = int(self.info.page_count)
        self.page_number = max(1, min(int(initial_page), self.page_count))

        if cache_dir is None:
            self.cache_dir = (
                Path(__file__).resolve().parents[2]
                / "cache"
                / "source_livre_consultation"
            )
        else:
            self.cache_dir = Path(cache_dir).expanduser().resolve()

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._bg = bg
        self._panel_bg = panel_bg
        self._fg = fg
        self._muted = muted
        self._accent = accent
        self._on_page_changed = on_page_changed
        self._page_trace_provider = page_trace_provider

        self._pil_original: Image.Image | None = None
        self._photo: ImageTk.PhotoImage | None = None
        self._resize_after: str | None = None
        self._key_bindings: list[tuple[str, str]] = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_canvas()
        self._bind_keyboard_navigation()

        self.bind("<Configure>", self._on_resize, add="+")
        self.bind("<Destroy>", self._on_destroy, add="+")
        self.after_idle(self.show_page)

    def _build_toolbar(self) -> None:
        # Bande d'identité de la page source. Le nom du fichier et le statut
        # éditorial sont volontairement regroupés au centre, hors de la page,
        # pour être lisibles au premier regard sans masquer le document auteur.
        bar = tk.Frame(self, bg=self._panel_bg, height=88)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(2, weight=1)
        bar.grid_rowconfigure(0, weight=1)

        self.prev_button = tk.Button(
            bar,
            text="‹",
            command=self.previous_page,
            bg=self._panel_bg,
            fg=self._fg,
            activebackground="#313A45",
            activeforeground=self._fg,
            relief="flat",
            bd=0,
            font=("Segoe UI", 18, "bold"),
            width=3,
            cursor="hand2",
        )
        self.prev_button.grid(row=0, column=0, padx=(8, 2), pady=5, sticky="ns")

        self.next_button = tk.Button(
            bar,
            text="›",
            command=self.next_page,
            bg=self._panel_bg,
            fg=self._fg,
            activebackground="#313A45",
            activeforeground=self._fg,
            relief="flat",
            bd=0,
            font=("Segoe UI", 18, "bold"),
            width=3,
            cursor="hand2",
        )
        self.next_button.grid(row=0, column=1, padx=2, pady=5, sticky="ns")

        identity = tk.Frame(bar, bg=self._panel_bg)
        identity.grid(row=0, column=2, sticky="nsew", padx=12, pady=(7, 6))
        identity.grid_columnconfigure(0, weight=1)
        identity.grid_rowconfigure(0, weight=1)
        identity.grid_rowconfigure(1, weight=1)
        identity.grid_rowconfigure(2, weight=1)

        self.title_label = tk.Label(
            identity,
            text=self.source.name,
            bg=self._panel_bg,
            fg=self._muted,
            font=("Segoe UI", 9),
            anchor="center",
        )
        self.title_label.grid(row=0, column=0, sticky="ew")

        self.type_current_label = tk.Label(
            identity,
            text="",
            bg=self._panel_bg,
            fg=self._fg,
            font=("Segoe UI", 9, "bold"),
            anchor="center",
        )
        self.type_current_label.grid(row=1, column=0, sticky="ew")

        self.type_initial_label = tk.Label(
            identity,
            text="",
            bg=self._panel_bg,
            fg=self._muted,
            font=("Segoe UI", 8),
            anchor="center",
        )
        self.type_initial_label.grid(row=2, column=0, sticky="ew")

        self.page_label = tk.Label(
            bar,
            text="",
            bg=self._panel_bg,
            fg=self._accent,
            font=("Segoe UI", 9, "bold"),
            width=14,
            anchor="e",
        )
        self.page_label.grid(row=0, column=3, padx=(4, 14), sticky="ns")

    def _refresh_type_trace(self) -> None:
        provider = self._page_trace_provider
        if not callable(provider):
            self.type_current_label.configure(text="")
            self.type_initial_label.configure(text="")
            return

        try:
            trace = provider(self.page_number)
        except Exception:
            trace = None

        if not trace:
            self.type_current_label.configure(text="")
            self.type_initial_label.configure(text="")
            return

        current = str(trace.get("current") or "Sans type").strip() or "Sans type"
        self.type_current_label.configure(text=f"Type actuel : {current}")

        if trace.get("modified"):
            initial = str(trace.get("initial") or "Sans type").strip() or "Sans type"
            self.type_initial_label.configure(text=f"Modifié depuis : {initial}")
        else:
            self.type_initial_label.configure(text="")

    def _build_canvas(self) -> None:
        self.canvas = tk.Canvas(
            self,
            bg=self._bg,
            bd=0,
            highlightthickness=0,
            takefocus=True,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")

        self.canvas.bind("<MouseWheel>", self._on_mousewheel, add="+")
        self.canvas.bind("<Button-4>", lambda _e: self.previous_page(), add="+")
        self.canvas.bind("<Button-5>", lambda _e: self.next_page(), add="+")
        self.canvas.bind("<Button-1>", lambda _e: self.canvas.focus_set(), add="+")

    def _bind_keyboard_navigation(self) -> None:
        top = self.winfo_toplevel()
        for sequence, callback in (
            ("<Left>", self._on_left_key),
            ("<Right>", self._on_right_key),
        ):
            bind_id = top.bind(sequence, callback, add="+")
            if bind_id:
                self._key_bindings.append((sequence, bind_id))

    def _on_destroy(self, event=None) -> None:
        if event is not None and event.widget is not self:
            return
        if self._resize_after is not None:
            try:
                self.after_cancel(self._resize_after)
            except Exception:
                pass
            self._resize_after = None
        top = self.winfo_toplevel()
        for sequence, bind_id in self._key_bindings:
            try:
                top.unbind(sequence, bind_id)
            except Exception:
                pass
        self._key_bindings.clear()

    def _on_left_key(self, _event=None) -> str:
        if not self.winfo_exists() or not self.winfo_viewable():
            return ""
        self.previous_page()
        return "break"

    def _on_right_key(self, _event=None) -> str:
        if not self.winfo_exists() or not self.winfo_viewable():
            return ""
        self.next_page()
        return "break"

    def _cache_path(self, page_number: int) -> Path:
        stem = self.source.stem.replace(" ", "_")
        return self.cache_dir / f"{stem}_page_{page_number:04d}.png"

    def _load_page_image(self, page_number: int) -> Image.Image:
        target = self._cache_path(page_number)
        if not target.is_file():
            render_pdf_page(
                self.source,
                page_number,
                target,
                max_width=1800,
            )
        with Image.open(target) as image:
            return image.convert("RGB").copy()

    def show_page(self, page_number: int | None = None) -> None:
        if page_number is not None:
            self.page_number = max(
                1,
                min(int(page_number), self.page_count),
            )

        self._pil_original = self._load_page_image(self.page_number)
        self.page_label.configure(
            text=f"Page {self.page_number} / {self.page_count}"
        )
        self._refresh_type_trace()
        if callable(self._on_page_changed):
            try:
                self._on_page_changed(self.page_number)
            except Exception:
                pass
        self.prev_button.configure(
            state="normal" if self.page_number > 1 else "disabled"
        )
        self.next_button.configure(
            state="normal" if self.page_number < self.page_count else "disabled"
        )
        self._draw_fitted()

    def previous_page(self) -> None:
        if self.page_number > 1:
            self.show_page(self.page_number - 1)

    def next_page(self) -> None:
        if self.page_number < self.page_count:
            self.show_page(self.page_number + 1)

    def _on_mousewheel(self, event) -> str:
        delta = int(getattr(event, "delta", 0))
        if delta > 0:
            self.previous_page()
        elif delta < 0:
            self.next_page()
        return "break"

    def _on_resize(self, _event=None) -> None:
        if self._resize_after is not None:
            try:
                self.after_cancel(self._resize_after)
            except Exception:
                pass
        self._resize_after = self.after(80, self._draw_fitted)

    def _draw_fitted(self) -> None:
        self._resize_after = None

        if self._pil_original is None:
            return

        cw = max(100, self.canvas.winfo_width())
        ch = max(100, self.canvas.winfo_height())
        margin = 28

        available_w = max(50, cw - margin * 2)
        available_h = max(50, ch - margin * 2)

        iw, ih = self._pil_original.size
        scale = min(
            available_w / max(1, iw),
            available_h / max(1, ih),
        )
        scale = max(0.05, scale)

        width = max(1, int(iw * scale))
        height = max(1, int(ih * scale))

        resized = self._pil_original.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )
        self._photo = ImageTk.PhotoImage(resized)

        x = cw // 2
        y = ch // 2

        self.canvas.delete("all")

        self.canvas.create_rectangle(
            x - width // 2 + 7,
            y - height // 2 + 8,
            x + width // 2 + 7,
            y + height // 2 + 8,
            fill="#101419",
            outline="",
        )
        self.canvas.create_image(
            x,
            y,
            image=self._photo,
            anchor="center",
        )
