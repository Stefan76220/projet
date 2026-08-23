from __future__ import annotations
import unittest
from src.gui_v3.book_canvas import BookCanvas

class DummyStatus:
    def __init__(self): self.value=''
    def set(self, value): self.value=value

class FamilyToolsTests(unittest.TestCase):
    def make_canvas(self):
        c=BookCanvas.__new__(BookCanvas)
        c.items=[{'id':'p1','type':'texte','plan_group':'g','gabarit_zones':[{'id':'z1','slot_key':'s1','kind':'text','x':.1,'y':.1,'w':.2,'h':.2}]}]
        c.groups=[{'id':'g','title':'Partie'}]
        c._selected_index=0
        c._gabarit_selected_zone_id='z1'
        c._gabarit_scope='page'
        c._gabarit_snap_enabled=True
        c.status_var=DummyStatus()
        c._save_order=lambda: None
        c.render=lambda: None
        c._emit_gabarit_page_changed=lambda: None
        c._emit_gabarit_selection_changed=lambda: None
        c._gabarit_mark_edited=lambda item: None
        c._gabarit_zone_target_indices=lambda: [0]
        c.gabarit_current_settings=lambda: {
            'margins_mm': {'top':15,'bottom':20,'inside':18,'outside':12},
            'bleed_mm': {'top':3,'right':4,'bottom':5,'left':6},
            'show_guides': True,
            'background':'#F1F1EE',
        }
        return c

    def test_rect_mm_roundtrip(self):
        c=self.make_canvas()
        self.assertTrue(c.gabarit_set_selected_zone_rect_mm(21,29.7,105,148.5))
        info=c.gabarit_selected_zone_info()
        self.assertEqual(info['occupation'],'free')
        self.assertAlmostEqual(info['rect_mm']['x'],21,places=1)
        self.assertAlmostEqual(info['rect_mm']['w'],105,places=1)

    def test_occupation_margins(self):
        c=self.make_canvas()
        self.assertTrue(c.gabarit_set_selected_zone_occupation('margins'))
        info=c.gabarit_selected_zone_info()
        self.assertEqual(info['occupation'],'margins')
        self.assertAlmostEqual(info['rect_mm']['x'],18,places=1)
        self.assertAlmostEqual(info['rect_mm']['y'],15,places=1)
        self.assertAlmostEqual(info['rect_mm']['w'],180,places=1)

    def test_occupation_bleed(self):
        c=self.make_canvas()
        self.assertTrue(c.gabarit_set_selected_zone_occupation('bleed'))
        info=c.gabarit_selected_zone_info()
        self.assertEqual(info['occupation'],'bleed')
        self.assertAlmostEqual(info['rect_mm']['x'],-6,places=1)
        self.assertAlmostEqual(info['rect_mm']['y'],-3,places=1)
        self.assertAlmostEqual(info['rect_mm']['w'],220,places=1)

    def test_align_to_margins(self):
        c=self.make_canvas()
        self.assertTrue(c.gabarit_align_selected_zone('right', reference='margins'))
        info=c.gabarit_selected_zone_info()
        self.assertAlmostEqual(info['rect_mm']['x'],156,places=1)

    def test_snap_profile(self):
        c=self.make_canvas()
        self.assertTrue(c.gabarit_set_snap_profile('margins',['left','hcenter','bad']))
        p=c.gabarit_snap_profile()
        self.assertEqual(p['reference'],'margins')
        self.assertEqual(p['anchors'],['left','hcenter'])

if __name__=='__main__': unittest.main()
