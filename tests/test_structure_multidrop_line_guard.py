from types import SimpleNamespace
import unittest

from src.gui_v3.book_canvas import BookCanvas


class FakeCanvas:
    def canvasy(self, y):
        return y
    def canvasx(self, x):
        return x


class FakeStatus:
    def __init__(self):
        self.value = ""
    def set(self, value):
        self.value = value


class MultiDropLineGuardTests(unittest.TestCase):
    def test_only_page_line_is_valid_drop_band(self):
        c = BookCanvas.__new__(BookCanvas)
        c.canvas = FakeCanvas()
        c._structure_page_line_bounds = (100.0, 220.0)
        self.assertTrue(c._structure_page_line_contains_event(SimpleNamespace(y=150)))
        self.assertTrue(c._structure_page_line_contains_event(SimpleNamespace(y=100)))
        self.assertTrue(c._structure_page_line_contains_event(SimpleNamespace(y=220)))
        self.assertFalse(c._structure_page_line_contains_event(SimpleNamespace(y=80)))
        self.assertFalse(c._structure_page_line_contains_event(SimpleNamespace(y=240)))

    def test_click_outside_line_cancels_instead_of_inserting(self):
        c = BookCanvas.__new__(BookCanvas)
        c._structure_pending_kind = "page"
        c._structure_pending_payload = {"type": "texte", "label": "Texte"}
        c._structure_update_hover_target = lambda event: None
        calls = []
        c.structure_cancel_tool = lambda: calls.append("cancel")
        c.status_var = FakeStatus()
        result = c._structure_apply_pending_event(SimpleNamespace(x=10, y=10))
        self.assertEqual(result, "break")
        self.assertEqual(calls, ["cancel"])
        self.assertEqual(c.status_var.value, "Dépôt multiple terminé.")


if __name__ == "__main__":
    unittest.main()
