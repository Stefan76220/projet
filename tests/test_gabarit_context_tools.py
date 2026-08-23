from __future__ import annotations

import unittest
from src.gui_v3.book_canvas import BookCanvas


class DummyStatus:
    def __init__(self):
        self.value = ""
    def set(self, value):
        self.value = value


class GabaritContextToolsTests(unittest.TestCase):
    def make_canvas(self):
        c = BookCanvas.__new__(BookCanvas)
        c.items = [{"id": "a", "type": "texte", "plan_group": "g"}]
        c.groups = [{"id": "g", "title": "Partie 1"}]
        c._selected_index = 0
        c._selected_group_id = "g"
        c._gabarit_scope = "page"
        c._gabarit_selected_zone_id = ""
        c._gabarit_snap_enabled = True
        c._work_mode = "gabarits"
        c.status_var = DummyStatus()
        c._save_order = lambda: None
        c.render = lambda: None
        c._emit_gabarit_page_changed = lambda: None
        c._emit_gabarit_selection_changed = lambda: None
        c._is_automatic_page = lambda item: False
        c._is_locked_page = lambda item: False
        c._type_of = lambda item: str(item.get("type") or "")
        c._page_type_label = lambda item, index: str(item.get("type") or "Page").title()
        c._item_group_id = lambda item: str(item.get("plan_group") or "")
        c._effective_double_page_rule = lambda item: False
        c._double_page_pair_id = lambda item: ""
        c._double_page_pair_members = lambda pair_id: []
        c._structure_work_number_span = lambda index: (index + 1, index + 1)
        c._structure_project_type = lambda: "livre_textuel"
        return c

    def test_selection_info_and_lock(self):
        c = self.make_canvas()
        self.assertTrue(c.gabarit_add_zone("text"))
        self.assertEqual(c.gabarit_selected_zone_info()["kind"], "text")
        self.assertTrue(c.gabarit_toggle_selected_zone_lock())
        self.assertTrue(c.gabarit_selected_zone_info()["locked"])

    def test_align(self):
        c = self.make_canvas()
        c.gabarit_add_zone("image")
        zone = c.items[0]["gabarit_zones"][0]
        zone.update({"x": .12, "y": .15, "w": .4, "h": .3})
        self.assertTrue(c.gabarit_align_selected_zone("center"))
        self.assertAlmostEqual(zone["x"], .3)

    def test_snap_toggle(self):
        c = self.make_canvas()
        self.assertFalse(c.gabarit_toggle_snap())
        self.assertFalse(c.gabarit_snap_enabled())
        self.assertTrue(c.gabarit_toggle_snap())

    def test_layer_move(self):
        c = self.make_canvas()
        c.gabarit_add_zone("text")
        first = c.items[0]["gabarit_zones"][0]["id"]
        c.gabarit_add_zone("image")
        second = c.items[0]["gabarit_zones"][1]["id"]
        c._gabarit_selected_zone_id = first
        self.assertTrue(c.gabarit_move_selected_zone_layer("front"))
        self.assertEqual(c.items[0]["gabarit_zones"][1]["id"], first)
        c._gabarit_selected_zone_id = second
        self.assertTrue(c.gabarit_move_selected_zone_layer("front"))


if __name__ == "__main__":
    unittest.main()
