from __future__ import annotations

import unittest

from src.gui_v3.book_canvas import BookCanvas


class GabaritNavigationTests(unittest.TestCase):
    def make_canvas(self):
        c = BookCanvas.__new__(BookCanvas)
        c.items = [
            {"id": "a", "type": "texte", "plan_group": "g"},
            {"id": "b", "type": "illustration", "plan_group": "g"},
            {"id": "c", "type": "chapitre", "plan_group": "g"},
            {"id": "d", "type": "texte", "plan_group": "g"},
            {"id": "e", "type": "page_blanche", "plan_group": "g", "automatic": True},
        ]
        c.groups = [{"id": "g", "title": "Partie 1"}]
        c._selected_index = 2
        c._selected_group_id = "g"
        c._gabarit_zoom = 230
        c._gabarit_pan_x = 31.0
        c._gabarit_pan_y = -14.0
        c._work_mode = "gabarits"
        c.render = lambda: None
        c._emit_gabarit_page_changed = lambda: None
        c._is_automatic_page = lambda item: bool(item.get("automatic"))
        c._is_locked_page = lambda item: False
        c._type_of = lambda item: str(item.get("type") or "")
        c._page_type_label = lambda item, index: str(item.get("type") or "Page").replace("_", " ").title()
        c._item_group_id = lambda item: str(item.get("plan_group") or "")
        c._effective_double_page_rule = lambda item: bool(item.get("double"))
        c._double_page_pair_id = lambda item: str(item.get("double_page_pair_id") or "")
        c._double_page_pair_members = lambda pair_id: [(i, item) for i, item in enumerate(c.items) if item.get("double_page_pair_id") == pair_id]
        c._structure_work_number_span = lambda index: (index + 1, index + (2 if c.items[index].get("double") else 1))
        c._structure_project_type = lambda: "livre_textuel"
        return c

    def test_page_change_keeps_zoom_and_pan(self):
        c = self.make_canvas()
        self.assertTrue(c.gabarit_navigate(1))
        self.assertEqual(c._selected_index, 3)
        self.assertEqual(c._gabarit_zoom, 230)
        self.assertEqual(c._gabarit_pan_x, 31.0)
        self.assertEqual(c._gabarit_pan_y, -14.0)

    def test_reset_zoom_returns_fit_baseline(self):
        c = self.make_canvas()
        c.gabarit_reset_zoom()
        self.assertEqual(c._gabarit_zoom, 100)
        self.assertEqual(c._gabarit_pan_x, 0.0)
        self.assertEqual(c._gabarit_pan_y, 0.0)

    def test_paired_pages_are_one_navigation_unit(self):
        c = self.make_canvas()
        c.items[1]["double_page_pair_id"] = "p"
        c.items[2]["double_page_pair_id"] = "p"
        units = c._gabarit_navigation_units()
        pair = next(unit for unit in units if unit["primary"] == 1)
        self.assertEqual(pair["indices"], (1, 2))
        self.assertTrue(pair["double"])

    def test_status_is_ready_for_context_strip(self):
        c = self.make_canvas()
        c.items[0]["gabarit_status"] = "termine"
        c.items[1]["gabarit_zones"] = [{"kind": "image"}]
        self.assertEqual(c._gabarit_status(c.items[0]), "termine")
        self.assertEqual(c._gabarit_status(c.items[1]), "en_cours")
        self.assertEqual(c._gabarit_status(c.items[2]), "non_commence")


if __name__ == "__main__":
    unittest.main()
