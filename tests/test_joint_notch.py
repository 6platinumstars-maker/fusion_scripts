import ast
import math
from pathlib import Path
from types import SimpleNamespace as N
import unittest
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]

class Collection(list):
    @property
    def count(self): return len(self)
    def add(self, value): self.append(value)
    def item(self, index): return self[index]

class JointNotchTests(unittest.TestCase):
    def execute(self, sign=1, bad_area=False):
        source=ROOT/'fusion_app/outer_shell_joint_notch.py'
        tree=ast.parse(source.read_text())
        tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        point=lambda x,y,z:N(x=x,y=y,z=z)
        made_lines=[]
        def line(a,b):
            result=N(startSketchPoint=a if hasattr(a,'geometry') else N(geometry=a),
                     endSketchPoint=b if hasattr(b,'geometry') else N(geometry=b))
            made_lines.append(result)
            return result
        plane=N()
        sketch=N(modelToSketchSpace=lambda p:point(p.y,p.z,0),
                 sketchToModelSpace=lambda p:point(-7.6795+sign*p.z,p.x,p.y),
                 sketchCurves=N(sketchLines=N(addByTwoPoints=line),
                 sketchCircles=N(addByCenterRadius=lambda p,r:N(centerSketchPoint=N(geometry=p)))))
        input_body=N(name='outer',volume=10,isSolid=True)
        data=N(setOneSideExtent=Mock())
        def add_cut(data):
            self.assertEqual(data.participantBodies,[input_body])
            input_body.volume=8
            return N()
        extrudes=N(createInput=Mock(return_value=data),add=Mock(side_effect=add_cut))
        root=N(sketches=N(add=lambda p:sketch),features=N(extrudeFeatures=extrudes))
        env={'math':math,'adsk':N(core=N(Point3D=N(create=point),ObjectCollection=N(create=Collection),ValueInput=N(createByReal=lambda x:x)),
              fusion=N(FeatureOperations=N(CutFeatureOperation='cut'),ExtentDirections=N(PositiveExtentDirection='positive',NegativeExtentDirection='negative'),DistanceExtentDefinition=N(create=lambda x:x))),
             'helpers':N(add_named_attribute=Mock(),set_body_identity=lambda b,n:setattr(b,'name',n)),
             'naming':N(BODY_OUTER_SHELL='outer'),
             'outer_shell':N(create_offset_plane_from_yz=Mock(return_value=plane)),
             'outer_shell_rectangle_cut':N(remaining_bodies=lambda originals,feature:originals)}
        exec(compile(tree,str(source),'exec'),env)
        reports=[];env['write_report']=lambda report:reports.append(dict(report)) or 'diagnostics'
        area=env['expected_area_mm2']()
        sketch.profiles=Collection([N(areaProperties=lambda:N(area=(area+(1 if bad_area else 0))/100))])
        if bad_area:
            with self.assertRaises(RuntimeError): env['cut'](root,{'outer':input_body})
            extrudes.add.assert_not_called()
        else:
            result=env['cut'](root,{'outer':input_body})
            self.assertIs(result['outer'],input_body)
            self.assertEqual(len(made_lines),6)
            data.setOneSideExtent.assert_called_once_with(4.0,'positive' if sign==1 else 'negative')
            self.assertAlmostEqual(reports[-1]['end_x_mm'],-36.795)
            self.assertEqual(reports[-1]['stage'],'cut_succeeded')
        return env

    def test_positive_x_and_reversed_sketch(self):
        self.execute(1);self.execute(-1)

    def test_bad_profile_area_stops_before_cut(self): self.execute(bad_area=True)

    def test_corrected_coordinates_and_union_area(self):
        env=self.execute()
        points=env['POINTS_MM']
        for key in ('B','E'): self.assertAlmostEqual(math.dist(points[key],points['A']),5)
        self.assertEqual(points['C'][2],15.495)
        self.assertEqual(points['D'][2],5.495)
        self.assertAlmostEqual(env['expected_area_mm2'](),220+95.645+12.5*math.pi)
        entry=(ROOT/'fusion_app/outer_shell_structure.py').read_text()
        self.assertLess(entry.index('outer_shell_notches.cut_upper_notch(root_comp'),entry.index('outer_shell_joint_notch.cut(root_comp'))

if __name__=='__main__': unittest.main()
