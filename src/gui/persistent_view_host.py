from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


class PersistentViewHost:
    """
    Hôte d'écrans persistants.

    Principe :
    - chaque écran possède son propre conteneur ;
    - l'écran actuellement visible reste affiché pendant la construction
      du suivant ;
    - le changement final se fait par lift(), sans destruction du parent ;
    - un écran déjà construit peut être réaffiché instantanément.
    """

    def __init__(
        self,
        parent,
        *,
        fg_color,
    ) -> None:
        self.frame = ctk.CTkFrame(
            parent,
            fg_color=fg_color,
            corner_radius=0,
        )
        self.frame.pack(fill="both", expand=True)

        self._fg_color = fg_color
        self._surfaces: dict[str, ctk.CTkFrame] = {}
        self._active_name: str | None = None

    @property
    def active_name(self) -> str | None:
        return self._active_name

    def surface(
        self,
        name: str,
    ) -> ctk.CTkFrame:
        surface = self._surfaces.get(name)

        if surface is not None:
            try:
                if surface.winfo_exists():
                    return surface
            except Exception:
                pass

        surface = ctk.CTkFrame(
            self.frame,
            fg_color=self._fg_color,
            corner_radius=0,
        )
        surface.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1,
        )
        surface.lower()

        self._surfaces[name] = surface
        return surface

    def rebuild(
        self,
        name: str,
        builder: Callable[[ctk.CTkFrame], None],
    ) -> ctk.CTkFrame:
        """
        Reconstruit un écran pendant qu'il reste derrière l'écran visible.
        """
        surface = self.surface(name)

        # Ne jamais exposer le conteneur vide.
        surface.lower()

        for child in tuple(surface.winfo_children()):
            child.destroy()

        builder(surface)

        # Termine les calculs de géométrie avant la bascule.
        surface.update_idletasks()
        return surface

    def show(
        self,
        name: str,
    ) -> ctk.CTkFrame:
        surface = self.surface(name)
        surface.lift()
        self._active_name = name
        return surface

    def has(
        self,
        name: str,
    ) -> bool:
        surface = self._surfaces.get(name)
        if surface is None:
            return False

        try:
            return bool(surface.winfo_exists())
        except Exception:
            return False

    def clear_surface(
        self,
        name: str,
    ) -> None:
        surface = self._surfaces.get(name)
        if surface is None:
            return

        for child in tuple(surface.winfo_children()):
            child.destroy()

    def drop(
        self,
        name: str,
    ) -> None:
        surface = self._surfaces.pop(name, None)
        if surface is None:
            return

        try:
            surface.destroy()
        except Exception:
            pass

        if self._active_name == name:
            self._active_name = None
