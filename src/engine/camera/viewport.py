from dataclasses import dataclass, field

from src.engine.camera.camera import Camera


@dataclass
class Viewport:
    """
    Interface entre la caméra et le reste du logiciel.

    Toutes les coordonnées du document sont exprimées en millimètres.
    Les coordonnées écran sont exprimées en pixels.
    """

    camera: Camera = field(default_factory=Camera)

    pixels_per_mm: float = 3.7795275591

    _listeners: list = field(default_factory=list, init=False, repr=False)

    # ------------------------------------------------------------------

    @property
    def zoom(self):
        return self.camera.zoom

    @zoom.setter
    def zoom(self, value):
        self.camera.set_zoom(value)

    # ------------------------------------------------------------------

    @property
    def offset_x_px(self):
        return self.camera.x

    @offset_x_px.setter
    def offset_x_px(self, value):
        self.camera.x = value

    # ------------------------------------------------------------------

    @property
    def offset_y_px(self):
        return self.camera.y

    @offset_y_px.setter
    def offset_y_px(self, value):
        self.camera.y = value

    # ------------------------------------------------------------------

    def add_listener(self, callback):

        if callback not in self._listeners:
            self._listeners.append(callback)

    # ------------------------------------------------------------------

    def remove_listener(self, callback):

        if callback in self._listeners:
            self._listeners.remove(callback)

    # ------------------------------------------------------------------

    def notify(self):

        for callback in self._listeners:
            callback()

    # ------------------------------------------------------------------

    def mm_to_px(self, value_mm):

        return value_mm * self.pixels_per_mm * self.camera.zoom

    # ------------------------------------------------------------------

    def px_to_mm(self, value_px):

        return value_px / (self.pixels_per_mm * self.camera.zoom)

    # ------------------------------------------------------------------

    def document_to_screen(self, x_mm, y_mm):

        return (
            self.mm_to_px(x_mm) + self.camera.x,
            self.mm_to_px(y_mm) + self.camera.y,
        )

    # ------------------------------------------------------------------

    def screen_to_document(self, x_px, y_px):

        return (
            self.px_to_mm(x_px - self.camera.x),
            self.px_to_mm(y_px - self.camera.y),
        )

    # ------------------------------------------------------------------

    def move(self, dx_px, dy_px):

        self.camera.move(dx_px, dy_px)
        self.notify()

    # ------------------------------------------------------------------

    def zoom_at(self, factor, center_x_px=0.0, center_y_px=0.0):
        """
        Pour l'instant, seul le niveau de zoom est modifié.

        Le véritable zoom sous le pointeur sera implémenté
        dans EditorCanvas où la position réelle de la page est connue.
        """

        ancien_zoom = self.camera.zoom

        self.camera.set_zoom(ancien_zoom * factor)

        if self.camera.zoom != ancien_zoom:
            self.notify()

    # ------------------------------------------------------------------

    def reset(self):

        self.camera.reset()
        self.notify()