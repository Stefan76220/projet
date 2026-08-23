from __future__ import annotations
import unittest
from pathlib import Path
from src.gui_v3.book_canvas import BookCanvas


class DummyVar:
    def __init__(self): self.value = ''
    def set(self, value): self.value = value


class DummyCanvas:
    def __init__(self): self.cursor = None
    def configure(self, **kwargs): self.cursor = kwargs.get('cursor', self.cursor)


def bare_canvas():
    c = BookCanvas.__new__(BookCanvas)
    c._work_mode = 'structure'
    c._structure_pending_kind = 'page'
    c._structure_pending_payload = {'type': 'texte', 'label': 'Texte'}
    c._structure_hover_target = None
    c._structure_page_auto_mode = None
    c._structure_action_mode = None
    c.status_var = DummyVar()
    c.canvas = DummyCanvas()
    c.render = lambda: None
    c.event_generate = lambda *args, **kwargs: None
    return c


class MultiDropTests(unittest.TestCase):
    def test_page_tool_stays_armed_after_successful_drop(self):
        c = bare_canvas()
        c._structure_update_hover_target = lambda event: ('page', 'g1', 0, 10)
        inserted = []
        c._structure_insert_page = lambda page_type, label, group_id, pos: inserted.append((page_type, label, group_id, pos)) or 0
        result = c._structure_apply_pending_event(object())
        self.assertEqual(result, 'break')
        self.assertEqual(c._structure_pending_kind, 'page')
        self.assertEqual(c.structure_pending_page_type(), 'texte')
        self.assertEqual(inserted, [('texte', 'Texte', 'g1', 0)])
        self.assertIn('dépôt multiple actif', c.status_var.value)
        self.assertEqual(c.canvas.cursor, 'crosshair')

    def test_multiple_successive_drops_use_same_payload(self):
        c = bare_canvas()
        targets = iter([('page', 'g1', 1, 10), ('page', 'g2', 3, 20), ('page', 'g2', 4, 30)])
        c._structure_update_hover_target = lambda event: next(targets)
        inserted = []
        c._structure_insert_page = lambda page_type, label, group_id, pos: inserted.append((page_type, group_id, pos)) or len(inserted)
        for _ in range(3):
            c._structure_apply_pending_event(object())
        self.assertEqual(inserted, [('texte', 'g1', 1), ('texte', 'g2', 3), ('texte', 'g2', 4)])
        self.assertEqual(c._structure_pending_kind, 'page')
        self.assertEqual(c.structure_pending_page_type(), 'texte')

    def test_escape_ends_multiple_drop(self):
        c = bare_canvas()
        self.assertEqual(c._structure_escape(), 'break')
        self.assertIsNone(c._structure_pending_kind)
        self.assertIsNone(c._structure_pending_payload)
        self.assertEqual(c.canvas.cursor, 'arrow')
        self.assertIn('terminé', c.status_var.value)

    def test_zone_c_second_click_toggle_is_present(self):
        source = (Path(__file__).resolve().parents[1] / 'src' / 'gui_v3' / 'app.py').read_text(encoding='utf-8')
        self.assertIn('Second clic sur la même brique', source)
        self.assertIn('structure_pending_page_type', source)
        self.assertIn('<<StructureToolChanged>>', source)


if __name__ == '__main__':
    unittest.main()
