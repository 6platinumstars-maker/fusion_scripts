import unittest
from types import SimpleNamespace as NS
from fusion_app import grip_solid_probe as p


def name(tag):return '面：'+tag+'：説明'


class ProbeTests(unittest.TestCase):
    def test_identifies_pairs_and_distinguishes_two_targets(self):
        tags=['SmV9','Con21','Con11','Con18','Other']
        names=list(map(name,tags));result={}
        def test(indices):
            selected={tags[i] for i in indices}
            return {'SmV9','Con11'}<=selected or {'Con21','Con18'}<=selected
        p.investigate(names,test,result)
        self.assertFalse(result['baseline_without_targets_failed'])
        groups=[set(g) for row in result['targets'] for g in row['failing_groups']]
        self.assertIn({name('SmV9'),name('Con11')},groups)
        self.assertIn({name('Con21'),name('Con18')},groups)

    def test_reduces_three_face_failure_without_claiming_pair_failure(self):
        tags=['SmV9','Con21','A','B','C','D','E']
        result={}
        p.investigate(list(map(name,tags)),lambda ids:{'SmV9','B','D'}<={tags[i] for i in ids},result)
        row=result['targets'][0]
        self.assertEqual(set(row['failing_groups'][0]),{name('SmV9'),name('B'),name('D')})
        self.assertEqual(result['targets'][1]['failing_groups'],[])

    def test_zero_cells_is_success_and_always_cancels(self):
        class Input:
            bRepCells=NS(count=0)
            cancelled=False
            def cancel(self):self.cancelled=True;return True
        inp=Input()
        result=p.probe_input(NS(createInput=lambda *a:inp),None,None)
        self.assertFalse(result['failed']);self.assertTrue(inp.cancelled)
        self.assertFalse(inp.isRemoveTools)
        self.assertEqual(result['cell_count'],0)

    def test_internal_error_is_recorded_and_cancellation_failure_stops(self):
        class Cells:
            @property
            def count(self):raise RuntimeError('InternalValidationError')
        for cancel_ok in (True,False):
            inp=NS(bRepCells=Cells(),cancel=lambda:cancel_ok)
            result=p.probe_input(NS(createInput=lambda *a:inp),None,None)
            self.assertTrue(result['failed'])
            self.assertIn('InternalValidationError',result['error'])
            self.assertEqual(bool(result.get('unsafe_to_continue')),not cancel_ok)

    def test_input_creation_failure_aborts_further_trials(self):
        result=p.probe_input(NS(createInput=lambda *a:None),None,None)
        self.assertTrue(result['unsafe_to_continue'])


if __name__=='__main__':unittest.main()
