from __future__ import annotations

import tkinter as tk

from src.gui_v3 import theme


class GlobalHoverManager:
    """Effet de survol commun à toute la V3.

    Le gestionnaire ne demande aucun enregistrement écran par écran :
    - tous les ``tk.Button`` sont pris en charge ;
    - toute zone qui annonce ``cursor='hand2'`` est considérée cliquable ;
    - les widgets créés plus tard (dialogues, listes récentes, etc.) profitent
      automatiquement du même comportement.

    ``V3Button`` garde son propre survol historique afin de ne pas empiler
    deux effets sur le même bouton.
    """

    def __init__(self, root: tk.Misc) -> None:
        self.root = root
        self._target: tk.Misc | None = None
        self._snapshots: dict[tk.Misc, dict[str, object]] = {}
        self._hover_bg: str | None = None
        self._press_bg: str | None = None

        # bind_all couvre l'Accueil, A/B/C, la barre de focus et les Toplevel.
        root.bind_all("<Motion>", self._on_motion, add="+")
        root.bind_all("<ButtonPress-1>", self._on_press, add="+")
        root.bind_all("<ButtonRelease-1>", self._on_release, add="+")
        root.bind("<Leave>", self._on_root_leave, add="+")

    # ------------------------------------------------------------------
    # Détection de la zone interactive
    # ------------------------------------------------------------------

    def _is_disabled(self, widget: tk.Misc) -> bool:
        try:
            if "state" in widget.keys():
                return str(widget.cget("state")) == "disabled"
        except Exception:
            pass
        return False

    def _cursor_is_hand(self, widget: tk.Misc) -> bool:
        try:
            return "cursor" in widget.keys() and str(widget.cget("cursor")) == "hand2"
        except Exception:
            return False

    def _resolve_target(self, widget: tk.Misc | None) -> tk.Misc | None:
        if widget is None:
            return None

        # V3Button possède déjà son survol propre dans app.py.
        if widget.__class__.__name__ == "V3Button":
            return None

        # Un vrai bouton a priorité sur ses parents.
        if isinstance(widget, tk.Button) and not self._is_disabled(widget):
            return widget

        candidate = None
        current = widget
        while current is not None:
            if current.__class__.__name__ == "V3Button":
                return None
            if isinstance(current, tk.Button):
                if not self._is_disabled(current):
                    return current
                return None
            if self._cursor_is_hand(current) and not self._is_disabled(current):
                # On conserve le parent cliquable le plus haut afin qu'une
                # carte entière réagisse même si la souris est sur son texte.
                candidate = current
            if current is self.root:
                break
            current = getattr(current, "master", None)
        return candidate

    # ------------------------------------------------------------------
    # Couleurs / snapshots
    # ------------------------------------------------------------------

    def _rgb(self, color: str) -> tuple[int, int, int]:
        try:
            r, g, b = self.root.winfo_rgb(color)
            return r // 257, g // 257, b // 257
        except Exception:
            return 48, 54, 64

    def _mix(self, a: str, b: str, amount: float) -> str:
        ar, ag, ab = self._rgb(a)
        br, bg, bb = self._rgb(b)
        amount = max(0.0, min(1.0, amount))
        r = round(ar * (1.0 - amount) + br * amount)
        g = round(ag * (1.0 - amount) + bg * amount)
        bl = round(ab * (1.0 - amount) + bb * amount)
        return f"#{r:02X}{g:02X}{bl:02X}"

    @staticmethod
    def _option(widget: tk.Misc, name: str):
        try:
            if name in widget.keys():
                return widget.cget(name)
        except Exception:
            pass
        return None

    def _descendants(self, widget: tk.Misc):
        yield widget
        try:
            children = widget.winfo_children()
        except Exception:
            children = []
        for child in children:
            yield from self._descendants(child)

    def _capture(self, target: tk.Misc) -> None:
        self._snapshots = {}
        for widget in self._descendants(target):
            data = {}
            for option in (
                "bg",
                "fg",
                "highlightbackground",
                "highlightcolor",
                "highlightthickness",
                "relief",
            ):
                value = self._option(widget, option)
                if value is not None:
                    data[option] = value
            if data:
                self._snapshots[widget] = data

    def _restore(self) -> None:
        for widget, data in list(self._snapshots.items()):
            try:
                widget.configure(**data)
            except Exception:
                pass
        self._snapshots = {}
        self._hover_bg = None
        self._press_bg = None

    def _discard_snapshot(self) -> None:
        self._snapshots = {}
        self._hover_bg = None
        self._press_bg = None

    def _apply(self, target: tk.Misc, *, pressed: bool = False) -> None:
        target_data = self._snapshots.get(target, {})
        base_bg = str(target_data.get("bg", self._option(target, "bg") or theme.PANEL_SOFT))
        accent = theme.ACCENT_BRIGHT if not pressed else theme.ACCENT
        amount = 0.18 if not pressed else 0.31
        new_bg = self._mix(base_bg, accent, amount)

        if pressed:
            self._press_bg = new_bg
        else:
            self._hover_bg = new_bg

        is_button = isinstance(target, tk.Button)
        is_label = isinstance(target, tk.Label)

        if is_button:
            options = {"bg": new_bg}
            if "fg" in target.keys():
                options["fg"] = theme.WHITE
            if "relief" in target.keys():
                options["relief"] = "sunken" if pressed else "raised"
            try:
                target.configure(**options)
            except Exception:
                pass
            return

        if is_label:
            try:
                target.configure(fg=theme.ACCENT_BRIGHT)
            except Exception:
                pass
            return

        # Pour une carte/zone : le fond de tous ses enfants qui partageaient
        # le même fond suit la carte. Les icônes/images gardent leur dessin.
        for widget, data in list(self._snapshots.items()):
            options = {}
            old_bg = data.get("bg")
            if old_bg is not None and str(old_bg) == base_bg:
                options["bg"] = new_bg

            if widget is target:
                old_ht = data.get("highlightthickness")
                try:
                    thickness = int(float(old_ht)) if old_ht is not None else 0
                except Exception:
                    thickness = 0
                if thickness > 0 and "highlightbackground" in data:
                    options["highlightbackground"] = theme.ACCENT_BRIGHT

            if options:
                try:
                    widget.configure(**options)
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # Événements
    # ------------------------------------------------------------------

    def _enter(self, target: tk.Misc) -> None:
        self._target = target
        self._capture(target)
        self._apply(target, pressed=False)

    def _leave_current(self) -> None:
        if self._target is not None:
            self._restore()
        self._target = None

    def _on_motion(self, event) -> None:
        target = self._resolve_target(getattr(event, "widget", None))
        if target is self._target:
            return
        self._leave_current()
        if target is not None:
            self._enter(target)

    def _on_press(self, event) -> None:
        target = self._resolve_target(getattr(event, "widget", None))
        if target is None or target is not self._target:
            return

        # Les cartes TomeLinea utilisent souvent <Button-1> directement :
        # leur état sélectionné est donc installé AVANT le bind_all. Si le
        # fond a changé depuis le simple survol, ce nouvel état devient la
        # base à préserver après le clic.
        try:
            current_bg = str(target.cget("bg")) if "bg" in target.keys() else ""
        except Exception:
            current_bg = ""
        if self._hover_bg and current_bg and current_bg != self._hover_bg:
            self._discard_snapshot()
            self._capture(target)

        self._apply(target, pressed=True)

    def _on_release(self, event) -> None:
        target = self._resolve_target(getattr(event, "widget", None))
        if target is None or target is not self._target:
            return

        # Les commandes de sélection peuvent modifier durablement la couleur
        # du widget (onglet actif, type de livre choisi). On laisse d'abord
        # leur binding terminer, puis on distingue cet état d'un simple clic.
        self.root.after_idle(lambda t=target: self._after_release(t))

    def _after_release(self, target: tk.Misc) -> None:
        if target is not self._target:
            return
        try:
            current_bg = str(target.cget("bg")) if "bg" in target.keys() else ""
        except Exception:
            return

        # Si la commande a installé un nouvel état visuel permanent,
        # il devient la nouvelle base du survol au lieu d'être écrasé.
        if current_bg not in {self._hover_bg or "", self._press_bg or ""}:
            self._discard_snapshot()
            self._capture(target)
            self._apply(target, pressed=False)
        else:
            self._apply(target, pressed=False)

    def _on_root_leave(self, event) -> None:
        if getattr(event, "widget", None) is self.root:
            self._leave_current()
