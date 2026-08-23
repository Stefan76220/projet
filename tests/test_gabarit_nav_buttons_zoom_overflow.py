from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.gui_v3.book_canvas import BookCanvas


class GabaritNavButtonsZoomOverflowTests(unittest.TestCase):
    def make_canvas(self):
        c = BookCanvas.__new__(BookCanvas)
        c._gabarit_zoom = 100
        c._gabarit_pan_x = 0.0
        c._gabarit_pan_y = 0.0
        c._work_mode = "gabarits"
        c.render = lambda: None
        return c

    def test_zoom_can_exceed_workspace_fit_baseline(self):
        c = self.make_canvas()
        c.gabarit_set_zoom(650)
        self.assertEqual(c._gabarit_zoom, 650)

    def test_pan_remains_available_when_zoomed_page_exceeds_B(self):
        c = self.make_canvas()
        c._gabarit_zoom = 300
        c._gabarit_pan_x = 9999.0
        c._gabarit_pan_y = -9999.0
        c._gabarit_clamp_pan(1200, 650, 1700, 2400)
        self.assertGreater(c._gabarit_pan_x, 0.0)
        self.assertLess(c._gabarit_pan_y, 0.0)
        self.assertLess(c._gabarit_pan_x, 9999.0)
        self.assertGreater(c._gabarit_pan_y, -9999.0)

    def test_navigation_button_activates_on_release_inside_same_square(self):
        c = self.make_canvas()
        c._gabarit_pressed_control = "next"
        c._gabarit_hover_control = "next"
        c._gabarit_hitboxes = {"next": (10.0, 10.0, 60.0, 60.0)}
        calls = []
        c.gabarit_navigate = lambda delta: calls.append(delta) or True
        c.canvas = SimpleNamespace(configure=lambda **kwargs: None)
        c._gabarit_zone_drag = None
        c._gabarit_drag_origin = None
        c._gabarit_pan_origin = None
        result = c._gabarit_release(SimpleNamespace(x=35, y=35))
        self.assertEqual(result, "break")
        self.assertEqual(calls, [1])
        self.assertEqual(c._gabarit_pressed_control, "")


if __name__ == "__main__":
    unittest.main()
