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
    c.status_var = DummyVar()
    c.render = lambda: None
    c.on_change = None
    return c

class PreGabaritsTests(unittest.TestCase):
    def test_incompatible_av_ap_create_two_autos(self):
        c = canvas([
            {'id':'A','type':'illustration','plan_group':'g1'},
            {'id':'B','type':'carte','plan_group':'g1'},
        ], data={'page_auto_type_rules':{
            'illustration':{'after':'illustration'},
            'carte':{'before':'page_blanche'},
        }})
        c._sync_structural_automatic_pages()
        autos=[x for x in c.items if c._is_automatic_page(x)]
        self.assertEqual([c._type_of(x) for x in autos], ['illustration','page_blanche'])
        self.assertTrue(any(r['code']=='AP' and r['source_id']=='A' for r in c._automatic_roles(autos[0])))
        self.assertTrue(any(r['code']=='AV' and r['source_id']=='B' for r in c._automatic_roles(autos[1])))
        self.assertFalse(any(x.get('automatic_type_conflict') for x in autos))

    def test_compatible_av_ap_still_merge(self):
        c = canvas([
            {'id':'A','type':'illustration','plan_group':'g1'},
            {'id':'B','type':'carte','plan_group':'g1'},
        ], data={'page_auto_type_rules':{
            'illustration':{'after':'page_blanche'},
            'carte':{'before':'page_blanche'},
        }})
        c._sync_structural_automatic_pages()
        autos=[x for x in c.items if c._is_automatic_page(x)]
        self.assertEqual(len(autos), 1)
        self.assertEqual({r['code'] for r in c._automatic_roles(autos[0])}, {'AP','AV'})

    def test_selection_is_reanchored_by_id_after_auto_disappears(self):
        c = canvas([
            {'id':'A','type':'texte','plan_group':'g1'},
            {'id':'B','type':'sommaire','plan_group':'g1'},
        ], data={'recto_verso_type_rules':{'sommaire':'recto'}})
        c._selected_page_ids={'B'}; c._selected_index=1; c._selected_group_id='g1'
        c._sync_structural_automatic_pages()
        self.assertEqual(c.items[c._selected_index]['id'], 'B')
        c.items[c._selected_index]['recto_verso_override']='__none__'
        c._sync_structural_automatic_pages()
        self.assertEqual(c.items[c._selected_index]['id'], 'B')

    def test_replace_type_keeps_id_and_clears_overrides(self):
        c = canvas([{
            'id':'A','type':'texte','plan_group':'g1',
            'page_auto_before_override':'page_blanche',
            'page_auto_after_override':'illustration',
            'recto_verso_override':'__none__',
            'double_page_override':'__none__',
        }])
        c._selected_page_ids={'A'}; c._selected_index=0; c._selected_group_id='g1'
        self.assertTrue(c.structure_replace_selected_page_type('chapitre'))
        source=next(x for x in c.items if x.get('id')=='A')
        self.assertEqual(c._type_of(source),'chapitre')
        for key in ('page_auto_before_override','page_auto_after_override','recto_verso_override','double_page_override'):
            self.assertNotIn(key, source)

    def test_gabarits_snapshot_reports_physical_structure(self):
        c = canvas([
            {'id':'A','type':'texte','plan_group':'g1'},
            {'id':'B','type':'illustration','plan_group':'g1'},
        ], data={'double_page_type_rules':{'illustration':True}})
        c._sync_structural_automatic_pages()
        snap=c.structure_gabarits_snapshot()
        self.assertEqual(snap['schema'],'tomelinea.structure.gabarits.v1')
        by_id={p['id']:p for p in snap['pages']}
        self.assertEqual(by_id['A']['physical_side'],'recto')
        # B needs a blank correction to start left if possible; source remains double in snapshot.
        self.assertTrue(by_id['B']['double_page'])
        self.assertIn(by_id['B']['physical_side'], {'verso_recto','recto'})
        self.assertGreaterEqual(snap['physical_page_count'], 3)

    def test_multi_move_keeps_source_order(self):
        c = canvas([
            {'id':'A','type':'texte','plan_group':'g1'},
            {'id':'B','type':'chapitre','plan_group':'g1'},
            {'id':'C','type':'texte','plan_group':'g1'},
            {'id':'D','type':'texte','plan_group':'g2'},
        ], groups=[{'id':'g1','title':'Partie 1'},{'id':'g2','title':'Partie 2'}], data={
            'page_auto_type_rules':{'chapitre':{'after':'page_blanche'}}
        })
        c._sync_structural_automatic_pages()
        auto_id=next(x['id'] for x in c.items if c._is_automatic_page(x))
        moved=c._move_selected_pages_to_group_position(['B','C'],'g2',1)
        self.assertEqual(moved,['B','C'])
        c._sync_structural_automatic_pages()
        sources=[x for x in c.items if not c._is_automatic_page(x)]
        self.assertEqual([x['id'] for x in sources], ['A','D','B','C'])
        self.assertEqual([x['plan_group'] for x in sources if x['id'] in {'B','C'}], ['g2','g2'])
        self.assertEqual(next(x['id'] for x in c.items if c._is_automatic_page(x)), auto_id)

if __name__ == '__main__': unittest.main()
