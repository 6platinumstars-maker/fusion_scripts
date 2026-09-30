import ast
from pathlib import Path
from types import SimpleNamespace as N
import unittest
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]

class BoreTests(unittest.TestCase):
    module_name = 'inner_shell_joint_bore.py'
    x_mm = -76.795
    radius_mm = 2.5

    def check_cut(self, sign, after=8):
        source=ROOT/'fusion_app'/self.module_name
        tree=ast.parse(source.read_text())
        tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        point=lambda x,y,z:N(x=x,y=y,z=z)
        circle_add=Mock(return_value=N())
        sketch=N(modelToSketchSpace=lambda p:p,
                 sketchToModelSpace=lambda p:point(self.x_mm/10+sign*p.z,p.x,p.y),
                 sketchCurves=N(sketchCircles=N(addByCenterRadius=circle_add)),
                 profiles=N(count=1,item=lambda i:'circle-profile'))
        plane=N();original=N(volume=10)
        result=N(volume=after,isSolid=True)
        data=N(setOneSideExtent=Mock())
        extrudes=N(createInput=Mock(return_value=data),add=Mock(return_value=N(bodies=N(count=1,item=lambda i:result))))
        root=N(sketches=N(add=lambda p:sketch),features=N(extrudeFeatures=extrudes))
        env={'adsk':N(core=N(Point3D=N(create=point),ValueInput=N(createByReal=lambda x:x)),
              fusion=N(ExtentDirections=N(PositiveExtentDirection='positive',NegativeExtentDirection='negative'),
                       FeatureOperations=N(CutFeatureOperation='cut'),DistanceExtentDefinition=N(create=lambda x:x))),
             'inner_shell':N(create_offset_plane_from_yz=Mock(return_value=plane)),
             'helpers':N(add_named_attribute=Mock(),set_body_identity=Mock()),
             'naming':N(BODY_INNER_SHELL='inner')}
        exec(compile(tree,str(source),'exec'),env)
        env['write_report']=lambda report:'diagnostics'
        if after==10:
            with self.assertRaises(RuntimeError):env['cut'](root,original)
            return
        self.assertIs(env['cut'](root,original),result)
        data.setOneSideExtent.assert_called_once_with(3.0,'positive' if sign==1 else 'negative')
        self.assertEqual(data.participantBodies,[original])
        extrudes.createInput.assert_called_once_with('circle-profile','cut')
        center,radius=circle_add.call_args.args
        self.assertAlmostEqual(center.x,self.x_mm/10)
        self.assertAlmostEqual(center.y,-.7201)
        self.assertAlmostEqual(center.z,1.0492)
        self.assertEqual(radius,self.radius_mm/10)
        self.assertAlmostEqual(env['CENTER_MM'][0]+env['DEPTH_MM'],self.x_mm+30)

    def test_correct_dimensions_target_and_positive_x(self):
        self.check_cut(1);self.check_cut(-1)

    def test_no_volume_change_stops(self):self.check_cut(1,10)

    def test_bore_after_joint_before_reference_publication(self):
        entry=(ROOT/'fusion_app/inner_shell_structure.py').read_text()
        self.assertLess(entry.index('inner_shell_joint.add_joint(root, body)'),entry.index('inner_shell_joint_bore.cut(root, body)'))
        self.assertLess(entry.index('inner_shell_joint_bore.cut(root, body)'),entry.index('reference_snapshot.publish(pending)'))

class BoreCTests(BoreTests):
    module_name = 'inner_shell_joint_bore_c.py'
    x_mm = -73.795
    radius_mm = 3.5

    def test_bore_after_joint_before_reference_publication(self):
        entry=(ROOT/'fusion_app/inner_shell_structure.py').read_text()
        self.assertLess(entry.index('inner_shell_joint_bore.cut(root, body)'),entry.index('inner_shell_joint_bore_c.cut(root, body)'))
        self.assertLess(entry.index('inner_shell_joint_bore_c.cut(root, body)'),entry.index('reference_snapshot.publish(pending)'))
        self.assertAlmostEqual(self.x_mm-BoreTests.x_mm,3.0)

if __name__=='__main__':unittest.main()
