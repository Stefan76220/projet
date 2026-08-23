from __future__ import annotations

import unittest
from src.gui_v3.book_canvas import BookCanvas


class DummyStatus:
    def __init__(self): self.value = ''
    def set(self, value): self.value = value


class GabaritToolsBaseTests(unittest.TestCase):
    def make_canvas(self):
        c = BookCanvas.__new__(BookCanvas)
        c.items = [
            {'id':'a','type':'texte','plan_group':'g'},
            {'id':'b','type':'texte','plan_group':'g'},
            {'id':'c','type':'illustration','plan_group':'g'},
        ]
        c.groups = [{'id':'g','title':'Partie 1'}]
        c._selected_index = 0
        c._selected_group_id = 'g'
        c._gabarit_scope = 'page'
        c._gabarit_selected_zone_id = ''
        c._work_mode = 'gabarits'
        c.status_var = DummyStatus()
        c._save_order = lambda: None
        c.render = lambda: None
        c._emit_gabarit_page_changed = lambda: None
        c._is_automatic_page = lambda item: bool(item.get('automatic'))
        c._is_locked_page = lambda item: False
        c._type_of = lambda item: str(item.get('type') or '')
        c._page_type_label = lambda item, index: str(item.get('type') or 'Page').title()
        c._item_group_id = lambda item: str(item.get('plan_group') or '')
        c._effective_double_page_rule = lambda item: bool(item.get('double'))
        c._double_page_pair_id = lambda item: str(item.get('double_page_pair_id') or '')
        c._double_page_pair_members = lambda pair_id: [(i, item) for i, item in enumerate(c.items) if item.get('double_page_pair_id') == pair_id]
        c._structure_work_number_span = lambda index: (index+1,index+1)
        c._structure_project_type = lambda: 'livre_textuel'
        return c

    def test_type_scope_propagates_margins(self):
        c = self.make_canvas(); c._gabarit_scope = 'type'
        self.assertTrue(c.gabarit_set_margins(20, 18, 16, 14))
        for idx in (0,1):
            self.assertEqual(c.items[idx]['gabarit_page_settings']['margins_mm']['top'], 20)
        self.assertNotIn('gabarit_page_settings', c.items[2])

    def test_type_scope_creates_corresponding_zones(self):
        c = self.make_canvas(); c._gabarit_scope = 'type'
        self.assertTrue(c.gabarit_add_zone('text'))
        za = c.items[0]['gabarit_zones'][0]
        zb = c.items[1]['gabarit_zones'][0]
        self.assertNotEqual(za['id'], zb['id'])
        self.assertEqual(za['slot_key'], zb['slot_key'])
        self.assertEqual(c._gabarit_selected_zone_id, za['id'])

    def test_center_selected_zone(self):
        c = self.make_canvas(); c.gabarit_add_zone('image')
        zone = c.items[0]['gabarit_zones'][0]
        zone.update({'x':0.02,'y':0.03,'w':0.4,'h':0.5})
        self.assertTrue(c.gabarit_center_selected_zone())
        self.assertAlmostEqual(zone['x'], 0.3)
        self.assertAlmostEqual(zone['y'], 0.25)

    def test_guides_toggle(self):
        c = self.make_canvas()
        self.assertTrue(c.gabarit_toggle_guides())
        self.assertFalse(c.items[0]['gabarit_page_settings']['show_guides'])
        self.assertTrue(c.gabarit_toggle_guides())
        self.assertTrue(c.items[0]['gabarit_page_settings']['show_guides'])


if __name__ == '__main__':
    unittest.main()
