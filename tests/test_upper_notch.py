"""Check notch coordinates and cut scope without the Fusion geometry kernel."""
import ast
from pathlib import Path
from types import SimpleNamespace as N
import unittest
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1]/'fusion_app/outer_shell_notches.py'


class UpperNotchTests(unittest.TestCase):
    def setup_cut(self, remaining_volume=9.0, count=1):
        tree=ast.parse(SOURCE.read_text())
        tree.body=[node for node in tree.body if not isinstance(node,(ast.Import,ast.ImportFrom))]
        added_lines=[]
        added_points=[]
        profiles=N(count=1,item=lambda i:'triangle-profile')
        def point_add(point):
            added_points.append(point)
            return 'apex-point'
        def sketch_add(plane):
            return N(modelToSketchSpace=lambda p:p,
                     sketchCurves=N(sketchLines=N(addByTwoPoints=lambda a,b:added_lines.append((a,b)))),
                     sketchPoints=N(add=point_add),profiles=profiles)
        result=N(isSolid=True,volume=remaining_volume)
        feature=N(bodies=N(count=count,item=lambda i:result))
        sections=[]
        loft_input=N(loftSections=N(add=sections.append))
        lofts=N(createInput=Mock(return_value=loft_input),add=Mock(return_value=feature))
        root=N(sketches=N(add=sketch_add),features=N(loftFeatures=lofts))
        planes=[]
        def make_plane(root,z,name):
            planes.append(z)
            return N()
        ns={'adsk':N(core=N(Point3D=N(create=lambda *xyz:xyz)),fusion=N(FeatureOperations=N(CutFeatureOperation='cut'))),
            'helpers':N(add_named_attribute=Mock(),set_body_identity=Mock()),
            'naming':N(BODY_OUTER_SHELL='outer'),
            'outer_shell_rectangle_cut':N(remaining_bodies=lambda originals,feature:[feature.bodies.item(i) for i in range(feature.bodies.count)]),
            'outer_shell':N(create_offset_plane_from_xy=make_plane)}
        exec(compile(tree,str(SOURCE),'exec'),ns)
        return ns,root,lofts,loft_input,sections,planes,added_lines,added_points

    def test_coordinates_and_only_outer_participates(self):
        ns,root,lofts,inp,sections,planes,lines,points=self.setup_cut()
        outer=N(volume=10.0)
        ns['cut_upper_notch'](root,{'outer':outer})
        lofts.createInput.assert_called_once_with('cut')
        self.assertEqual(inp.participantBodies,[outer])
        self.assertEqual(sections,['triangle-profile','apex-point'])
        self.assertEqual(planes,[-6.0,29.233])
        expected=[(-7.6795,1.8768,-.6),(-7.6795,3.22,-.6),(-6.7298,3.22,-.6)]
        for actual,target in zip([line[0] for line in lines],expected):
            for a,b in zip(actual,target): self.assertAlmostEqual(a,b)
        for a,b in zip(points[0],(-7.6795,3.2233,2.9233)): self.assertAlmostEqual(a,b)

    def test_no_cut_and_empty_results_are_not_reported_as_success(self):
        for volume,count in ((10.0,1),(9.0,0)):
            ns,root,*_=self.setup_cut(volume,count)
            with self.assertRaises(RuntimeError): ns['cut_upper_notch'](root,{'outer':N(volume=10.0)})


if __name__=='__main__': unittest.main()
