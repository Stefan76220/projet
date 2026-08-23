from types import SimpleNamespace
import unittest

from src.gui_v3.book_canvas import BookCanvas


class FakeWidget:
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return self.path


class OutsideClickTests(unittest.TestCase):
    def make_canvas(self):
        c = BookCanvas.__new__(BookCanvas)
        c.canvas = FakeWidget(".app.book.canvas")
        c.structure_command_bar = FakeWidget(".app.book.bar")
        c._structure_palette_widget = FakeWidget(".app.zonec.active")
        c._structure_pending_kind = "page"
        c._structure_action_mode = None
        c._title_editor = None
        calls = []
        c.structure_cancel_tool = lambda: calls.append("cancel")
        c._structure_reset_action = lambda: calls.append("reset_action")
        c.after_idle = lambda fn: fn()
        return c, calls

    def test_external_click_cancels_multidrop(self):
        c, calls = self.make_canvas()
        c._structure_global_click(SimpleNamespace(widget=FakeWidget(".app.header.somewhere")))
        self.assertEqual(calls, ["cancel"])

    def test_click_in_canvas_keeps_multidrop(self):
        c, calls = self.make_canvas()
        c._structure_global_click(SimpleNamespace(widget=FakeWidget(".app.book.canvas.child")))
        self.assertEqual(calls, [])

    def test_click_on_active_type_keeps_until_card_handler(self):
        c, calls = self.make_canvas()
        c._structure_global_click(SimpleNamespace(widget=FakeWidget(".app.zonec.active.label")))
        self.assertEqual(calls, [])

    def test_click_elsewhere_in_zone_c_cancels(self):
        c, calls = self.make_canvas()
        c._structure_global_click(SimpleNamespace(widget=FakeWidget(".app.zonec.empty")))
        self.assertEqual(calls, ["cancel"])


if __name__ == "__main__":
    unittest.main()
