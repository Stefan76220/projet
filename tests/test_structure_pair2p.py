from __future__ import annotations
import unittest
from src.gui_v3.book_canvas import BookCanvas

class DummyVar:
    def __init__(self): self.value=''
    def set(self, value): self.value=value


def canvas(items, groups=None, data=None):
    c = BookCanvas.__new__(BookCanvas)
    c.items = [dict(x) for x in items]
    c.groups = [dict(x) for x in (groups or [{'id':'g1','title':'Partie 1'}])]
    c._data = dict(data or {})
    c._data.setdefault('page_auto_type_rules', {})
    c._data.setdefault('recto_verso_type_rules', {})
    c._data.setdefault('double_page_type_rules', {})
    c.project = None
    c._structure_rule_sync_in_progress = False
    c._structure_selection_kind = 'page'
    c._selected_page_ids = set()
    c._selected_index = None
    c._selected_group_id = None
    c._structure_recto_verso_armed = False
    c._structure_rule_target = ''
    c._structure_rule_remove_pending = ''
    c._structure_double_pair_pending = None
    c.status_var = DummyVar()
    c.render = lambda: None
    c.on_change = None
    return c


def select(c, *ids):
    c._selected_page_ids=set(ids)
    c._selected_index=next(i for i,x in enumerate(c.items) if x.get('id')==ids[0])
    c._selected_group_id=c.items[c._selected_index].get('plan_group')

class Pair2PTests(unittest.TestCase):
    def test_pair_two_pages_requires_confirmation_and_adds_parity_auto(self):
        c=canvas([
            {'id':'A','type':'texte','plan_group':'g1'},
            {'id':'B','type':'illustration','plan_group':'g1'},
        ])
        select(c,'A','B')
        self.assertFalse(c.structure_toggle_selected_double_page_pair())
        self.assertIsNotNone(c._structure_double_pair_pending)
        self.assertTrue(c.structure_toggle_selected_double_page_pair())
        a=next(x for x in c.items if x.get('id')=='A')
        b=next(x for x in c.items if x.get('id')=='B')
        self.assertEqual(c._double_page_pair_id(a), c._double_page_pair_id(b))
        self.assertEqual(c._double_page_pair_role(a),'left')
        self.assertEqual(c._double_page_pair_role(b),'right')
        autos=[x for x in c.items if c._is_automatic_page(x)]
        self.assertEqual(len(autos),1)
        self.assertIn('DP',{r['code'] for r in c._automatic_roles(autos[0])})
        self.assertEqual([x['id'] for x in c.items if not c._is_automatic_page(x)],['A','B'])

    def test_pair_after_one_page_needs_no_correction(self):
        c=canvas([
            {'id':'X','type':'texte','plan_group':'g1'},
            {'id':'A','type':'texte','plan_group':'g1'},
            {'id':'B','type':'illustration','plan_group':'g1'},
        ])
        select(c,'A','B')
        c.structure_toggle_selected_double_page_pair(); c.structure_toggle_selected_double_page_pair()
        self.assertFalse([x for x in c.items if c._is_automatic_page(x)])
        snap=c.structure_gabarits_snapshot()
        by={p['id']:p for p in snap['pages']}
        self.assertEqual(by['A']['physical_side'],'verso')
        self.assertEqual(by['B']['physical_side'],'recto')

    def test_dissociate_pair_requires_confirmation(self):
        pair='DP-TEST'
        c=canvas([
            {'id':'A','type':'texte','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'left','double_page_pair_peer_id':'B'},
            {'id':'B','type':'illustration','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'right','double_page_pair_peer_id':'A'},
        ])
        select(c,'A','B')
        self.assertFalse(c.structure_toggle_selected_double_page_pair())
        self.assertEqual(c._structure_double_pair_pending['action'],'unpair')
        self.assertTrue(c.structure_toggle_selected_double_page_pair())
        for x in c.items:
            if not c._is_automatic_page(x):
                self.assertFalse(c._double_page_pair_id(x))

    def test_non_adjacent_pages_cannot_pair(self):
        c=canvas([
            {'id':'A','type':'texte','plan_group':'g1'},
            {'id':'X','type':'texte','plan_group':'g1'},
            {'id':'B','type':'illustration','plan_group':'g1'},
        ])
        select(c,'A','B')
        ctx=c._selected_double_page_pair_context()
        self.assertFalse(ctx['valid'])

    def test_pair_rejects_internal_av_ap_requirement(self):
        c=canvas([
            {'id':'A','type':'texte','plan_group':'g1'},
            {'id':'B','type':'illustration','plan_group':'g1'},
        ], data={'page_auto_type_rules':{'texte':{'after':'page_blanche'}}})
        select(c,'A','B')
        ctx=c._selected_double_page_pair_context()
        self.assertFalse(ctx['valid'])
        self.assertIn('AV/AP',ctx['reason'])

    def test_later_internal_auto_rule_does_not_break_pair(self):
        pair='DP-TEST'
        c=canvas([
            {'id':'A','type':'texte','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'left','double_page_pair_peer_id':'B'},
            {'id':'B','type':'illustration','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'right','double_page_pair_peer_id':'A'},
        ], data={'page_auto_type_rules':{'texte':{'after':'page_blanche'}}})
        c._sync_structural_automatic_pages()
        sources=[x for x in c.items if not c._is_automatic_page(x)]
        self.assertEqual([x['id'] for x in sources],['A','B'])
        # one correction may exist before A for parity, never between A and B
        ia=next(i for i,x in enumerate(c.items) if x.get('id')=='A')
        ib=next(i for i,x in enumerate(c.items) if x.get('id')=='B')
        self.assertEqual(ib, ia+1)
        self.assertTrue(next(x for x in c.items if x.get('id')=='A').get('double_page_pair_conflict'))

    def test_existing_av_before_pair_can_be_followed_by_required_parity_correction(self):
        pair='DP-TEST'
        c=canvas([
            {'id':'X','type':'texte','plan_group':'g1'},
            {'id':'A','type':'chapitre','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'left','double_page_pair_peer_id':'B'},
            {'id':'B','type':'illustration','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'right','double_page_pair_peer_id':'A'},
        ], data={'page_auto_type_rules':{'chapitre':{'before':'page_blanche'}}})
        c._sync_structural_automatic_pages()
        ia=next(i for i,x in enumerate(c.items) if x.get('id')=='A')
        # X = recto, AV blank = verso, correction blank = recto, then A = verso.
        self.assertEqual(sum(1 for x in c.items[:ia] if c._is_automatic_page(x)),2)
        self.assertFalse(next(x for x in c.items if x.get('id')=='A').get('double_page_pair_conflict'))

    def test_dragging_one_member_expands_to_whole_pair(self):
        pair='DP-TEST'
        c=canvas([
            {'id':'A','type':'texte','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'left','double_page_pair_peer_id':'B'},
            {'id':'B','type':'illustration','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'right','double_page_pair_peer_id':'A'},
        ])
        c._drag_selected_page_ids={'A'}
        c._drag_start_index=0
        self.assertEqual(c._drag_selected_source_ids(),['A','B'])

    def test_clone_complete_pair_gets_new_pair_and_peer_ids(self):
        pair='DP-OLD'
        originals=[
            {'id':'A','type':'texte','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'left','double_page_pair_peer_id':'B'},
            {'id':'B','type':'illustration','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'right','double_page_pair_peer_id':'A'},
        ]
        clones=[dict(originals[0],id='C'),dict(originals[1],id='D')]
        c=canvas(originals)
        c._rewire_cloned_double_page_pairs(originals,clones)
        self.assertNotEqual(clones[0]['double_page_pair_id'],pair)
        self.assertEqual(clones[0]['double_page_pair_id'],clones[1]['double_page_pair_id'])
        self.assertEqual(clones[0]['double_page_pair_peer_id'],'D')
        self.assertEqual(clones[1]['double_page_pair_peer_id'],'C')

    def test_gabarits_snapshot_exposes_pair_identity(self):
        pair='DP-TEST'
        c=canvas([
            {'id':'A','type':'texte','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'left','double_page_pair_peer_id':'B'},
            {'id':'B','type':'illustration','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'right','double_page_pair_peer_id':'A'},
        ])
        c._sync_structural_automatic_pages()
        snap=c.structure_gabarits_snapshot()
        by={p['id']:p for p in snap['pages']}
        self.assertTrue(by['A']['paired_double_page'])
        self.assertTrue(by['B']['paired_double_page'])
        self.assertEqual(by['A']['double_page_pair_role'],'left')
        self.assertEqual(by['B']['double_page_pair_role'],'right')
        self.assertEqual(by['A']['double_page_pair_id'],by['B']['double_page_pair_id'])


    def test_later_typewide_2p_rule_keeps_existing_pair_as_exception(self):
        pair='DP-TEST'
        c=canvas([
            {'id':'A','type':'texte','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'left','double_page_pair_peer_id':'B'},
            {'id':'B','type':'illustration','plan_group':'g1','double_page_pair_id':pair,'double_page_pair_role':'right','double_page_pair_peer_id':'A'},
            {'id':'C','type':'texte','plan_group':'g1'},
        ])
        select(c,'C')
        self.assertTrue(c.structure_apply_double_page_rule())
        a=next(x for x in c.items if x.get('id')=='A')
        cpage=next(x for x in c.items if x.get('id')=='C')
        self.assertEqual(a.get('double_page_override'),'__none__')
        self.assertFalse(c._effective_double_page_rule(a))
        self.assertTrue(c._effective_double_page_rule(cpage))
        self.assertEqual(c._double_page_pair_id(a),pair)

if __name__=='__main__': unittest.main()
