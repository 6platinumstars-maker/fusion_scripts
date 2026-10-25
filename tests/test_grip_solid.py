import math
import unittest
from types import SimpleNamespace as NS
from fusion_app import grip_solid as s


class Cells:
    def __init__(self,bodies):self.bodies=bodies;self.count=len(bodies)
    def item(self,i):return NS(cellBody=self.bodies[i])


class SolidTests(unittest.TestCase):
    def test_selection_excludes_con2_con10_and_keeps_originals(self):
        bodies=[NS(name='グリップ接続面：'+n+'：接続',isSolid=False,isLightBulbOn=True)
                for n in ('Con1','Con2','Con6','Con10','Con12','Con16','Con20','Con21')]
        root=NS(bRepBodies=bodies)
        self.assertEqual(s.source_surfaces(root),[b for b in bodies if not s.excluded_from_solid(b)])
        self.assertEqual(len(root.bRepBodies),8)
        self.assertTrue(all(b.isLightBulbOn for b in bodies))

    def test_old_saved_design_is_rejected_before_copy(self):
        old=[NS(name='固定面：Fx4：外殻円柱側面')]
        with self.assertRaisesRegex(RuntimeError,'Fx6'):
            s.validate_source_version(old)
        with self.assertRaisesRegex(RuntimeError,'Fx4'):
            s.validate_source_version(old+[NS(name='固定面：Fx22：Fx5指定4頂点接続面')])
        current=[NS(name='固定面：Fx4：上下円弧接続曲面 (1)'),
                 NS(name='固定面：Fx5：指定4頂点統合面'),
                 NS(name='固定面：Fx6：統合・指定5頂点切り取り面')]
        s.validate_source_version(current)
        for removed in ('Fx22','Fx23'):
            with self.assertRaises(RuntimeError):s.validate_source_version(current+[NS(name='固定面：'+removed+'：旧面')])

    def test_direct_mode_never_removes_existing_history_or_bodies(self):
        def design(bodies=0,timeline=0):
            return NS(designType='parametric',timeline=NS(count=timeline),
                      rootComponent=NS(bRepBodies=NS(count=bodies),occurrences=NS(count=0),sketches=NS(count=0)))
        empty=design();s.configure_new_target(empty,'direct')
        self.assertEqual(empty.designType,'direct')
        for existing in (design(bodies=1),design(timeline=1)):
            with self.assertRaises(RuntimeError):s.configure_new_target(existing,'direct')
            self.assertEqual(existing.designType,'parametric')

    def test_lazy_cell_failure_is_cancelled_without_masking_original_error(self):
        class BadCells:
            @property
            def count(self):raise RuntimeError('InternalValidationError')
        for cancel_fails in (False,True):
            class Input:
                bRepCells=BadCells()
                cancelled=False
                def cancel(self):
                    self.cancelled=True
                    if cancel_fails:raise RuntimeError('cancel failed')
            inp=Input();report={}
            with self.assertRaisesRegex(RuntimeError,'InternalValidationError'):
                s.prepare_fill(NS(createInput=lambda *args:inp),None,None,report)
            self.assertTrue(inp.cancelled)
            self.assertFalse(inp.isRemoveTools)
            self.assertEqual(report['stage'],'boundary_fill_compute_cells')
            self.assertEqual('cancel_error' in report,cancel_fails)

    def test_valid_cells_keep_tools_until_selection(self):
        inp=NS(bRepCells=Cells([NS(isSolid=True,volume=2.)]))
        actual,cells,volumes=s.prepare_fill(NS(createInput=lambda *args:inp),None,None,{})
        self.assertIs(actual,inp)
        self.assertFalse(inp.isRemoveTools)
        self.assertEqual(volumes,[2000.])

    def test_only_enclosing_surfaces_are_selected_even_if_hidden(self):
        names=['固定面：Fx4：上下円弧接続曲面','半変動面：SmV1：接続',
               'グリップ幅面：AL2：幅10mm','グリップ接続面：Con1：接続',
               '参考面：Ref1：内殻側面','参考線：Ref12：曲線','その他']
        bodies=[NS(name=n,isSolid=False,isLightBulbOn=False) for n in names]
        bodies.append(NS(name='固定面：誤ったソリッド',isSolid=True))
        root=NS(bRepBodies=bodies)
        self.assertEqual(s.source_surfaces(root),bodies[:4])
        self.assertTrue(all(not b.isLightBulbOn for b in bodies[:7]))
        with self.assertRaises(RuntimeError):s.source_surfaces(NS(bRepBodies=bodies[4:]))

    def test_closed_cell_volumes_and_ambiguous_candidates(self):
        self.assertEqual(s.cell_volumes(Cells([])),[])
        cells=Cells([NS(isSolid=True,volume=1.2),NS(isSolid=True,volume=.1)])
        self.assertEqual(s.cell_volumes(cells),[1200,100])
        for body in (None,NS(isSolid=False),NS(isSolid=True,volume=0),
                     NS(isSolid=True,volume=-1),NS(isSolid=True,volume=math.nan)):
            with self.assertRaises(RuntimeError):s.cell_volumes(Cells([body]))


if __name__=='__main__':unittest.main()

class StitchSelectionTests(unittest.TestCase):
    def test_fixed_part_three_only(self):
        from fusion_app.grip_surface_names import display_name
        for identifier in ('Fx2','Fx3'):
            for part in (1,2,3):
                self.assertEqual(s.excluded_from_solid(NS(name=display_name(identifier,part))),part==3)
        self.assertFalse(s.excluded_from_solid(NS(name='固定面：Fx13：三角面')))

    def test_reject_surface_multiple_bodies_and_bad_volume(self):
        good=NS(isSolid=True,volume=96.907851)
        self.assertIs(s.validate_stitched_result([good]),good)
        for bodies in ([],[good,good],[NS(isSolid=False,volume=0)],
                       [NS(isSolid=True,volume=float('nan'))],[NS(isSolid=True,volume=0)]):
            with self.assertRaises(RuntimeError):s.validate_stitched_result(bodies)

class StitchResultInspectionTests(unittest.TestCase):
    def test_null_feature_requires_actual_solid(self):
        body=NS(name='result',isSolid=True,faces=NS(count=70),volume=96.907851)
        report={}
        self.assertIs(s.inspect_stitch_result(None,NS(bRepBodies=[body]),report),body)
        self.assertFalse(report['stitch_feature_returned'])
        self.assertAlmostEqual(report['result_bodies'][0]['volume_mm3'],96907.851)
        surface=NS(name='surface',isSolid=False,faces=NS(count=1))
        with self.assertRaisesRegex(RuntimeError,'ソリッド数：0'):
            s.inspect_stitch_result(None,NS(bRepBodies=[surface]*69),report)
        self.assertEqual(len(report['result_bodies']),69)
